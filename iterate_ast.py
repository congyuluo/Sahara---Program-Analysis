from pycparser import parse_file, c_generator
from pycparser.c_ast import Node, UnaryOp, ArrayRef, StructRef, Assignment, FuncCall, ID, ExprList, Constant, Cast, Typename, PtrDecl, TypeDecl, IdentifierType

from copy import deepcopy
import re

from globals import c_altered_loc, c_processed_loc, c_altered_suffix, c_wrapper_funcs, c_probe_includes, c_auto_gen_notes, c_atexit_func, c_ptr_deref_func, c_funcCall_param_func, c_wrapperFunc_set

# Table storing ID -> dereference instances
deref_table = dict()
# Table storing ID -> External funcCall parameter logs
funcCall_param_table = dict()
# ID_count
ID_count = 0
# FuncCall param index
funcCall_param_index = 0


class DerefInstance:
    def __init__(self, str_rep: str, coord: str, ID: int):
        self.str_rep = str_rep
        self.coord = coord
        self.ID = ID

    def __str__(self):
        return f'{self.str_rep} at {self.coord} with ID {self.ID}'


class FuncCallParamInstance:
    def __init__(self, funcCallName: str, coord: str, paramIndex: int, ID: int):
        self.funcCallName = funcCallName
        self.coord = coord
        self.paramIndex = paramIndex
        self.ID = ID

    def __str__(self):
        return f'{self.funcCallName} with parameter index {self.paramIndex} and ID {self.ID}'

    def str_full(self):
        return f'{self.funcCallName} at {self.coord} with parameter index {self.paramIndex} and ID {self.ID}'

def next_ID() -> int:
    global ID_count
    next_ID = ID_count
    ID_count += 1
    return next_ID


def is_ptr_dereference(node: Node):
    return isinstance(node, UnaryOp) and node.op == '*'


def is_array_dereference(node: Node):
    return isinstance(node, ArrayRef)


def is_struct_dereference(node: Node):
    return isinstance(node, StructRef)


def is_dereference(node: Node):
    return is_ptr_dereference(node) or is_array_dereference(node) or is_struct_dereference(node)


def is_log_func(node: Node):
    return isinstance(node, FuncCall) and node.name.name in c_wrapperFunc_set


def get_base_address(node: Node) -> Node:
    if is_ptr_dereference(node):
        return node.expr
    elif is_array_dereference(node) or is_struct_dereference(node):
        return node.name
    # Raise error
    raise Exception('Not a pointer dereference')


def print_deref_table(dt: dict):
    print('------Dereference table:------')
    if len(dt) == 0:
        print('Empty')
    for i in dt:
        print(f'ID: {i}, {dt[i]}')


def print_funcCall_param_table(fpt: dict, full=False):
    print('------FuncCall parameter table:------')
    if len(fpt) == 0:
        print('Empty')
    for i in fpt:
        if full:
            print(f'ID: {i}, {fpt[i].str_full()}')
        else:
            print(f'ID: {i}, {fpt[i]}')

def is_funcCall(node: Node) -> bool:
    return isinstance(node, FuncCall)


def get_funcCallName(node: Node) -> str:
    return node.name.name


def alter_source(file_loc: str, includes: [], user_func_names: set, debug=False) -> (dict, dict):
    # Initiate AST & generator
    ast = parse_file(filename=c_processed_loc+file_loc)
    generator = c_generator.CGenerator()

    # Define function to alter base address
    def alter_base_address(node: Node) -> Node:
        # Add dereference instance to table
        new_id = next_ID()
        deref_table[new_id] = DerefInstance(generator.visit(node), node.coord, new_id)
        return Assignment('=', node,
                          FuncCall(ID(c_ptr_deref_func), ExprList([deepcopy(node), Constant('int', str(new_id))])))

    # Define function to alter parameter
    def alter_param(node: Node, id: int) -> Node:
        """Alter individual funcCall parameter with wrapperFunc"""
        temp = Typename(name=None, quals=[], align=None, type=PtrDecl(quals=[],
                                                                      type=TypeDecl(declname=None, quals=[], align=None,
                                                                                    type=IdentifierType(
                                                                                        names=['void']))))
        return Assignment('+', node,
                          FuncCall(ID(c_funcCall_param_func), ExprList([Cast(temp, deepcopy(node)), Constant('int', str(id))])))

    # Define function to alter function call
    def alter_funcCall(node: Node):
        """Alter funcCall parameters with wrapperFunc"""
        if is_funcCall(node):
            # Iterate over ExprList
            if node.args: # If not empty
                curr_funcName = get_funcCallName(node)
                curr_nodeCoord = node.coord
                global funcCall_param_index
                for i in range(len(node.args.exprs)):
                    # Alter node
                    node.args.exprs[i] = alter_param(node.args.exprs[i], funcCall_param_index)
                    # Add funcCall param instance to table
                    funcCall_param_table[funcCall_param_index] = FuncCallParamInstance(curr_funcName, curr_nodeCoord, i, funcCall_param_index)
                    # Increment funcCall param index
                    funcCall_param_index += 1
            return
        raise Exception('Not a function call')

    # Define function to alter node
    def alter_node(node: Node) -> Node:
        if is_ptr_dereference(node):
            node.expr = alter_base_address(get_base_address(node))
        elif is_array_dereference(node) or is_struct_dereference(node):
            node.name = alter_base_address(get_base_address(node))
        else:
            # Raise error
            raise Exception('Not a pointer dereference')

    # Define recursive function to iterate through AST
    def iterate_ast(node: Node, debug=False):
        if is_log_func(node):
            return
        is_deref = False
        if debug:
            print('Curr node: ' + generator.visit(node))
            if is_dereference(node):
                print('\nType: Struct dereference')
                print('Expression:  ' + generator.visit(node))
                print('Base address:' + generator.visit(get_base_address(node)))
        if is_ptr_dereference(node):
            alter_node(node)
        elif is_array_dereference(node):
            alter_node(node)
        elif is_struct_dereference(node):
            alter_node(node)
        elif is_funcCall(node) and (get_funcCallName(node) not in user_func_names):
            # External function call
            alter_funcCall(node)
        if debug and is_deref:
            print('Altered AST :' + generator.visit(ast))
        for (child_name, child) in node.children():
            iterate_ast(child, debug=debug)

    # Iterate through AST and alter it
    iterate_ast(ast, debug=debug)

    # Add file includes
    altered_source = c_auto_gen_notes
    for include in includes:
        altered_source += include + '\n'
    altered_source += '\n'

    # Add probe headers
    for probe_include in c_probe_includes:
        altered_source += probe_include + '\n'
    altered_source += '\n'

    # Generate the resulting source code
    altered_source += generator.visit(ast)

    # Modify function names
    for (func_name, wrapper_name) in c_wrapper_funcs:
        altered_source = re.sub(func_name, wrapper_name, altered_source)

    # Inject at-exit function
    matches = re.finditer(r'main\(.*\)( |\n)*{', altered_source)
    # Find last character index of last match
    last_char_index = None
    for match in matches:
        last_char_index = match.end() - 1
    if last_char_index is None:
        # Raise error
        raise Exception('No main function found')
    # Inject function
    injecting_index = last_char_index + 1
    altered_source = altered_source[:injecting_index] + c_atexit_func + altered_source[injecting_index:]

    # Write the content to the destination file
    with open(c_altered_loc + file_loc.split('.')[0] + c_altered_suffix, 'w') as dest_file:
        dest_file.write(altered_source)

    return deref_table, funcCall_param_table
