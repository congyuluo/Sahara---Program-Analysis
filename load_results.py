from globals import c_profiled_loc, c_alloc_type, c_deref_type, c_realloc_type, c_free_type, c_generic_type, c_source_loc
from processing import scope, print_scope_table, print_func_table
from iterate_ast import DerefInstance, FuncCallParamInstance, print_deref_table, print_funcCall_param_table
import pickle


class runtime_node:
    def __init__(self, code: str, index: int, timestamp: int):
        self.code = code
        self.index = index
        self.timestamp = timestamp


class alloc_node(runtime_node):
    def __init__(self, code: str, index: int, timestamp: int, alloc_id: int):
        super().__init__(code, index, timestamp)
        self.alloc_id = alloc_id

    def __str__(self):
        return f'{self.code} at {self.index} with allocation[{self.alloc_id}]'


class deref_node(runtime_node):
    def __init__(self, code: str, index: int, timestamp: int, alloc_id: int):
        super().__init__(code, index, timestamp)
        self.alloc_id = alloc_id

    def __str__(self):
        return f'{self.code} at {self.index} with allocation[{self.alloc_id}]'


class realloc_node(runtime_node):
    def __init__(self, code: str, index: int, timestamp: int, dealloc_id: int, alloc_id: int):
        super().__init__(code, index, timestamp)
        self.dealloc_id = dealloc_id
        self.alloc_id = alloc_id

    def __str__(self):
        return f'{self.code} at {self.index} with deallocation[{self.dealloc_id}] and allocation[{self.alloc_id}]'


class free_node(runtime_node):
    def __init__(self, code: str, index: int, timestamp: int, dealloc_id: int):
        super().__init__(code, index, timestamp)
        self.dealloc_id = dealloc_id

    def __str__(self):
        return f'{self.code} at {self.index} with deallocation[{self.dealloc_id}]'


class generic_node(runtime_node):
    def __init__(self, code: str, index: int, timestamp: int):
        super().__init__(code, index, timestamp)

    def __str__(self):
        return f'{self.code} at {self.index}'


def print_runtime_result(rt: []):
    for node in rt:
        print(node)


def print_alloc_table(alloc_table: dict()):
    print('------Allocation Table------')
    for alloc_id in alloc_table:
        print(f'alloc[{alloc_id}] = {alloc_table[alloc_id][:-1]}, {"Freed" if alloc_table[alloc_id][-1] else "Not Freed"}')


def load_allocation_table() -> dict():
    result = dict()
    # Open file
    with open(c_profiled_loc + 'allocTable.cymp', 'r') as f:
        for line in f:
            fields = line.strip().split(',')
            result[int(fields[0])] = (int(fields[1], 16), int(fields[2]), bool(int(fields[3])))
    return result


def load_runtime_result() -> []:
    result = []
    # Open file
    with open(c_profiled_loc + 'runtime.cymp', 'r') as f:
        for line in f:
            fields = line.strip().split(',')
            instr = fields[0]
            if instr in c_alloc_type:
                if len(fields) != 4:
                    raise Exception(f'Invalid alloc instruction {instr}')
                result.append(alloc_node(instr, int(fields[1]), fields[2], int(fields[3])))
            elif instr in c_deref_type:
                if len(fields) != 4:
                    raise Exception(f'Invalid deref instruction {instr}')
                result.append(deref_node(instr, int(fields[1]), fields[2], int(fields[3])))
            elif instr in c_realloc_type:
                if len(fields) != 5:
                    raise Exception(f'Invalid realloc instruction {instr}')
                result.append(realloc_node(instr, int(fields[1]), fields[2], int(fields[3]), int(fields[4])))
            elif instr in c_free_type:
                if len(fields) != 4:
                    raise Exception(f'Invalid free instruction {instr}')
                result.append(free_node(instr, int(fields[1]), fields[2], int(fields[3])))
            elif instr in c_generic_type:  # code, index, timstamp
                if len(fields) != 3:
                    raise Exception(f'Invalid generic instruction {instr}')
                result.append(generic_node(instr, int(fields[1]), fields[2]))
            else:
                raise Exception(f'Invalid instruction {instr}')
    return result


def import_all() -> (dict, [], dict, dict, dict, dict):
    try:
        alloc_table = load_allocation_table()  # Dict
    except:
        raise Exception('Error loading allocation table')

    try:
        runtime_result = load_runtime_result()  # List
    except:
        raise Exception('Error loading runtime result')

    # Unpickle all tables
    try:
        with open(c_profiled_loc + 'call_table.pkl', 'rb') as f:
            call_table = pickle.load(f)
    except:
        raise Exception('Error loading call table')

    try:
        with open(c_profiled_loc + 'deref_table.pkl', 'rb') as f:
            deref_table = pickle.load(f)
    except:
        raise Exception('Error loading deref table')

    try:
        with open(c_profiled_loc + 'func_table.pkl', 'rb') as f:
            func_table = pickle.load(f)
    except:
        raise Exception('Error loading func table')

    try:
        with open(c_profiled_loc + 'scope_table.pkl', 'rb') as f:
            scope_table = pickle.load(f)
    except:
        raise Exception('Error loading scope table')

    return alloc_table, runtime_result, call_table, scope_table, deref_table, func_table


def print_foreground(text, color_code):
    foreground_color = f"\033[{color_code}m"
    reset = "\033[0m"
    print(f"{foreground_color}{text}{reset}", end="")


def print_highlighted(text, background_color_code):
    background_color = f"\033[{background_color_code}m"
    reset = "\033[0m"
    print(f"{background_color}{text}{reset}", end="")


def print_highlighted_source(source: str, scope_table: dict):
    # Build enter coords and exits coords
    enter_coords = {scope_table[key].enter_coord : key for key in scope_table}
    exit_coords = {scope_table[key].exit_coord : key for key in scope_table}

    scope_frames = []
    line, index = 1, 1
    # Print line number
    print_foreground(f'#{line}\t| ', 31)
    # Variable to handle proper highlighting of closing braces
    exiting_scope = False
    for s in source:
        # Printing current char
        if exiting_scope:
            print_foreground(s, 32 + len(scope_frames) + 1)
            if s == '}':
                exiting_scope = False
        else:
            if len(scope_frames) == 0:
                print(s, end='')
            else:
                print_foreground(s, 32 + len(scope_frames))
        # Increment counts
        if s == '\n':
            line += 1
            index = 0
        index += 1
        # Check scope enter
        if f'{line}:{index}' in enter_coords:
            scope_frames.append(enter_coords[f'{line}:{index}'])
            # Print scope name
            print_highlighted(f'SCOPE({scope_frames[-1]})', 42)
        # Check scope exit
        if f'{line}:{index}' in exit_coords:
            if scope_frames.pop() != exit_coords[f'{line}:{index}']:
                raise Exception('Scope mismatch')
            exiting_scope = True
        # Print line number
        if s == '\n':
            print_foreground(f'#{line}\t| ', 31)
    print()


def process_runtime_result(print_result=False, print_runtime=False, print_tracking=False, print_highlight_source=True) -> dict:
    """Iterates through the runtime result and returns a modified scope table"""
    # Use import all
    alloc_table, runtime_result, call_table, scope_table, deref_table, func_table = import_all()

    if print_highlight_source:
        # Load source
        with open(c_source_loc + 'sample.c', 'r') as f:
            source = f.read()
        print_highlighted_source(source, scope_table)

    if print_runtime:
        print_runtime_result(runtime_result)
    if print_result:
        print_alloc_table(alloc_table)
        print_scope_table(scope_table)
        print_deref_table(deref_table)
        print_func_table(func_table)
        print_funcCall_param_table(call_table)

    scope_frame = []
    main_func = None
    # Iterate through runtime result
    for node in runtime_result:
        # Scope enter
        if node.code == 'SENT':
            if main_func is None:
                main_func = node.index
            scope_frame.append(node.index)
            # Add a new empty list to the current scope's runtime table
            scope_table[node.index].runtime_table[len(scope_table[node.index].runtime_table)] = []
            if print_tracking:
                print(f'Entering scope {node.index}')
                print(f'Scope frame: {scope_frame}')
        # Scope exit
        elif node.code == 'SEXT':
            if scope_frame.pop() != node.index:
                raise Exception(f'Scope frame exit mismatch at {node.index}')
            if print_tracking:
                print(f'Exiting scope {node.index}')
                print(f'Scope frame: {scope_frame}')
        # Handle function returns
        elif node.code == 'RETN':
            if main_func is None:
                raise Exception(f'Returning outside of main function')
            # If returning from a main function
            if scope_frame[-1] == main_func:
                if print_tracking:
                    print(f'Returning from main function')
                return scope_table, alloc_table
            else:
                if print_tracking:
                    print(f'Returning from function {scope_frame[-1]}')
                while scope_frame[-1] != main_func:
                    scope_frame.pop()
        elif node.code == 'EXIT':
            return scope_table, alloc_table
        else: # Every type of operation except scope change
            # Append node to runtime list of the latest entrance of the current scope
            scope_table[scope_frame[-1]].runtime_table[len(scope_table[scope_frame[-1]].runtime_table)-1].append(node)

    return scope_table, alloc_table


def print_scope_table_data(scope_table: dict, alloc_table: dict):
    def interpret_scope(s: scope):
        entrances = []
        # Iterate over entrance
        for i in range(len(s.runtime_table)):
            curr_deref_amount = 0
            curr_alloc_amound = 0
            curr_free_amount = 0
            curr_runtime_list = s.runtime_table[i]

            deref_blocks = set()
            alloc_blocks = set()
            free_blocks = set()
            # Iterate over runtime list
            for node in curr_runtime_list:
                if isinstance(node, deref_node):
                    deref_blocks.add(node.alloc_id)
                elif isinstance(node, alloc_node):
                    alloc_blocks.add(node.alloc_id)
                elif isinstance(node, realloc_node):
                    alloc_blocks.add(node.alloc_id)
                    free_blocks.add(node.dealloc_id)
                elif isinstance(node, free_node):
                    free_blocks.add(node.dealloc_id)
            # Iterate over blocks
            for block_id in deref_blocks:
                curr_deref_amount += alloc_table[block_id][1]
            for block_id in alloc_blocks:
                curr_alloc_amound += alloc_table[block_id][1]
            for block_id in free_blocks:
                curr_free_amount += alloc_table[block_id][1]

            entrances.append((curr_deref_amount, curr_alloc_amound, curr_free_amount))
        return entrances

    for id in scope_table:
        curr_scope = scope_table[id]
        print(curr_scope)
        stats = interpret_scope(curr_scope)
        for i, s in enumerate(stats):
            print(f'Entrance #{i}: ')
            if s[0] > 0:
                print(f'\t{s[0]} bytes dereferences', end='')
            if s[1] > 0:
                print(f'\t{s[1]} bytes allocations', end='')
            if s[2] > 0:
                print(f'\t{s[2]} bytes frees', end='')
            if s[0] == 0 and s[1] == 0 and s[2] == 0:
                print(f'\tNo memory action', end='')
            print()
        print()


if __name__ == '__main__':
    resulting_scope_table, alloc_table = process_runtime_result(print_result=False, print_runtime=False, print_tracking=False)
    print_scope_table_data(resulting_scope_table, alloc_table)

