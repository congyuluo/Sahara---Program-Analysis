import os
import subprocess

from errors import *
from ms_interpret import interpret_massif_output
from gprof_interpret import interpret_gprof_result

program_files = set(['gprof_executable', 'massif_executable', 'gmon.out'])

# Location of source code / executable
# working_directory = '/home/congyu/Desktop/profiler_test_folder'

# Location of sourcecode
sourcecode_list = ['sampleprogram.c']
# Program arguments
program_arguments = ''

# Callgrind CPU profiling arguments
callgrind_options = ''
# Massif memory profiling arguments
massif_options = ''

# Change working dir
# os.chdir(working_directory)


def cleanup():
    previous_output_files = [i for i in os.listdir() if i in program_files or i.startswith('massif.')]
    for f in previous_output_files:
        os.remove(f)


def gcc_compile(arg_list: []):
    if '' in arg_list:
        arg_list.remove('')
    out = subprocess.Popen(arg_list, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout, stderr = out.communicate()
    if (stderr is None) and ('error' not in stdout.decode()):
        pass
    else:
        print(stdout.decode())
        raise CompilationError()


def execute(arg_list: [], error: Exception, out_title=None):
    if '' in arg_list:
        arg_list.remove('')
    out = subprocess.Popen(arg_list, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout, stderr = out.communicate()
    if out_title is not None:
        print(f'------{out_title}------')
        print(stdout.decode())
        print('----------------------------')
    if stderr is None:
        pass
    else:
        raise error()
    return stdout.decode()


if __name__ == "__main__":
    # Delete prior files
    cleanup()
    print("Removed previous output files")

    # Compile GProf Executable
    print("Compiling sourcecode")
    gcc_compile(['gcc', '-Wall', '-pg'] + sourcecode_list + ['-o', 'gprof_executable'])
    gcc_compile(['gcc'] + sourcecode_list + ['-o', 'massif_executable'])
    print(f'Compilation successful')

    # Perform CPU profiling with valgrind
    print("GProf CPU Profiling")
    arg_list = ['./gprof_executable']
    execute(arg_list, GProfExecutionError)

    # Retrieve profiling result
    print("Retrieving profiling result")
    arg_list = ['gprof', '-p', '-b', 'gprof_executable', 'gmon.out']
    cpu_profiling_file = execute(arg_list, GProfExecutionError)

    # Interpret gprof result
    print("Interpreting CPU result")
    cpu_profile_result = interpret_gprof_result(cpu_profiling_file)

    # Perform Memory profiling with massif
    print("Massif Memory Profiling")
    arg_list = ['valgrind', '--tool=massif', '--detailed-freq=1', '--massif-out-file=massif.out.00000', massif_options,
                './' + 'massif_executable', program_arguments]
    result = execute(arg_list, ValgrindExecutionError)

    # Interpret profiling result
    print("Interpreting memory result")
    memory_profile_result = interpret_massif_output('massif.out.00000')

    # Cleanup
    cleanup()
    print("Removed output files")

    # Print results
    print("CPU Profiling Result:")
    print("Format| name : [%time, cumulative seconds, self seconds, calls, self Ts/call, total Ts/call]")
    print(cpu_profile_result)

    print("Memory Profiling Result:")
    print("Format| name: [Allocated memory at each snapshot]")
    print(memory_profile_result)

