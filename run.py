from processing import preprocess, print_scope_table, print_func_table
from iterate_ast import alter_source, print_deref_table, print_funcCall_param_table
from globals import c_profiled_loc
import pickle

if __name__ == '__main__':
    # Define source code
    source = 'sample.c'

    # Preprocess source code
    func_table, scope_table, includes = preprocess(source)

    # Get set of userfunc names
    user_func_names = set([func_table[i] for i in func_table])

    # Alter source code
    deref_table, call_table = alter_source('sample_processed.c', includes, user_func_names)

    print_func_table(func_table)
    print_scope_table(scope_table)
    print_deref_table(deref_table)
    print_funcCall_param_table(call_table)

    # Pickle the tables
    with open(c_profiled_loc+'deref_table.pkl', 'wb') as f:
        pickle.dump(deref_table, f)
    with open(c_profiled_loc+'call_table.pkl', 'wb') as f:
        pickle.dump(call_table, f)
    with open(c_profiled_loc+'func_table.pkl', 'wb') as f:
        pickle.dump(func_table, f)
    with open(c_profiled_loc+'scope_table.pkl', 'wb') as f:
        pickle.dump(scope_table, f)
