import re
from globals import c_source_loc, c_processed_loc, c_processed_suffix, c_scope_enter_func, c_scope_exit_func, c_return_func
from pycparser import c_parser
from pycparser.c_ast import Node, Struct, FuncDef


class scope:
    def __init__(self, ID: int, level: int, enter_coord: str, exit_coord=None):
        self.ID = ID
        self.level = level
        self.enter_coord = enter_coord
        self.exit_coord = exit_coord
        self.runtime_table = dict()

    def add_exit_coord(self, exit_coord: str):
        self.exit_coord = exit_coord

    def __str__(self):
        return f'ID: {self.ID}, level: {self.level}, enter_coord: {self.enter_coord}, exit_coord: {self.exit_coord}'


def locate_index(line: int, index: int, source: str) -> int:
    line_count = 1
    index_count = 1
    total_count = 0
    for i in source:
        if line_count == line and index_count == index:
            return total_count
        if i == '\n':
            line_count += 1
            index_count = 0
        index_count += 1
        total_count += 1
    return -1


def next_opening_bracket(source: str, start: int) -> int:
    curr_index = start
    while curr_index < len(source):
        if source[curr_index] == '{':
            return curr_index
        curr_index += 1
    return -1


def find_struct_ranges(ast: Node, source: str) -> set:
    struct_defs = []

    def iterate_ast(node: Node):
        if isinstance(node, Struct):
            struct_defs.append((node.coord.line, node.coord.column))

        for (child_name, child) in node.children():
            iterate_ast(child)

    iterate_ast(ast)
    # Find actual index
    struct_defs = [locate_index(line, index, source) for (line, index) in struct_defs]
    if -1 in struct_defs:
        raise Exception('Struct definition not found')
    # Find opening bracket
    struct_defs = [next_opening_bracket(source, i) for i in struct_defs]
    if -1 in struct_defs:
        raise Exception('Opening bracket not found')

    def find_range(start: int) -> int:
        curr_index = start + 1
        scope_level = 1
        while (scope_level > 0) and curr_index < len(source):
            if source[curr_index] == '{':
                scope_level += 1
            elif source[curr_index] == '}':
                scope_level -= 1
            curr_index += 1
        if scope_level != 0:
            raise Exception('Scope level mismatch')
        return curr_index - 1

    return [(i, find_range(i)) for i in struct_defs]


def get_scope_table(source: str, ranges: []) -> (str, dict):
    """Return the altered source code and scope table"""
    # Define table to store scope enter/exit. ID -> (Enter/Exit, sourcecode line: index)
    scope_table = dict()

    # Define resulting source code
    result_source = ''

    # Define scope level
    scope_level = 0
    # Define scope ID
    id_count = 0

    curr_line = 1
    curr_index = 1

    scope_stack = []

    def in_struct_range(index: int) -> bool:
        """Check if index is in struct range"""
        for (start, end) in ranges:
            if start <= index <= end:
                return True
        return False

    # Iterate over source code
    for global_index, i in enumerate(source):
        if in_struct_range(global_index): # Encountered struct range
            result_source += i
            if i == '\n':
                curr_line += 1
                curr_index = 0
            curr_index += 1
        else:
            if i == '{':  # Encountered scope enter
                result_source += i
                # Initiate new scope
                new_scope = scope(id_count, scope_level, f'{curr_line}:{curr_index}')
                scope_table[id_count] = new_scope
                scope_stack.append(new_scope)
                # Update ID count
                id_count += 1
                # Update scope level
                scope_level += 1
                # Add scope enter prob
                result_source += f'\n{c_scope_enter_func}({new_scope.ID});\n'
            elif i == '}':  # Encountered scope exit
                # Update scope level
                scope_level -= 1
                # Check scope level
                if scope_stack[-1].level != scope_level:
                    raise Exception('Scope level mismatch')
                # Update scope exit coord
                scope_stack[-1].add_exit_coord(f'{curr_line}:{curr_index}')
                # Add scope exit prob
                result_source += f'\n{c_scope_exit_func}({scope_stack[-1].ID});\n'
                result_source += i
                # Pop scope from stack
                scope_stack.pop()
            elif i == '\n':  # New line
                result_source += i
                curr_line += 1
                curr_index = 0
            else:
                result_source += i
            curr_index += 1

    return result_source, scope_table


def print_scope_table(scope_table: dict):
    """Print scope table"""
    print('------Scope table:------')
    if len(scope_table) == 0:
        print('Empty')
    for i in scope_table:
        print(scope_table[i])


def print_func_table(func_table: dict):
    """Print function table"""
    print('------Function table:------')
    if len(func_table) == 0:
        print('Empty')
    for i in func_table:
        print(f'ID: {i}, {func_table[i]}')


def is_funcDef(node: Node) -> bool:
    return isinstance(node, FuncDef)


def get_funcDefName(node: Node) -> str:
    if is_funcDef(node):
        return node.decl.name
    raise Exception('Not a function definition')


def get_func_table(ast: Node) -> dict:
    """Return a dict containing the function ID and name"""
    # GNU C's function declaration within a function is not supported
    func_table = dict()

    def iterate_ast(node: Node):
        if is_funcDef(node):
            func_table[len(func_table)] = get_funcDefName(node)
            return

        for (child_name, child) in node.children():
            iterate_ast(child)

    iterate_ast(ast)
    return func_table


def add_return_stmt(source: str) -> str:
    """Add probes to return statements"""
    # Find all matches using finditer()
    matches = re.finditer(r'return', source)
    # Get the index the first char of all matches
    insert_positions = [i.start() for i in matches]
    # Insert probes
    added_length = 0
    for i in insert_positions:
        source = source[:i+added_length] + f'\n{c_return_func}();\n' + source[i+added_length:]
        added_length += len(f'\n{c_return_func}();\n')
    return source


def preprocess(file_loc: str) -> (dict, dict, []):
    """Preprocess work on input source code"""
    # Read the content of the source file
    with open(c_source_loc+file_loc, 'r') as src_file:
        content = src_file.read()

    # Match all includes
    includes = re.findall(r'#include.*', content)

    # Remove all imports
    content = re.sub(r'#include.*', '', content)

    # Remove all comments
    content = re.sub(r'//.*', '', content)

    # parse source code
    parser = c_parser.CParser()
    ast = parser.parse(content, filename='<none>')

    # Build function table
    func_table = get_func_table(ast)

    # Find struct ranges
    struct_ranges = find_struct_ranges(ast, content)

    # Insert prob to scope enter & exits
    content, scope_table = get_scope_table(content, struct_ranges)

    # Insert prob to return stmt
    content = add_return_stmt(content)

    # Write the content to the destination file
    with open(c_processed_loc+file_loc.split('.')[0]+c_processed_suffix, 'w') as dest_file:
        dest_file.write(content)

    return func_table, scope_table, includes
