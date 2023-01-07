import os
import subprocess

from errors import *

# Location of source code / executable
working_directory = '/home/congyu/Desktop/profiler_test_folder'

# Location of executable
executable_filename = 'massif_test'
# Program arguments
program_arguments = ''

# Callgrind CPU profiling arguments
callgrind_options = ''
# Massif memory profiling arguments
massif_options = ''

# Change working dir
os.chdir(working_directory)

# Delete prior files
previous_output_files = [i for i in os.listdir() if i.startswith('massif.') or i.startswith('callgrind.')]
for f in previous_output_files:
    os.remove(f)
print("Removed previous output files")

# Perform CPU profiling with valgrind
print("Callgrind CPU Profiling")
arg_list = ['valgrind', '--tool=callgrind', callgrind_options, './' + executable_filename, program_arguments]
arg_list.remove('')
out = subprocess.Popen(arg_list, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
stdout, stderr = out.communicate()
print('------Callgrind Output------')
print(stdout.decode())
print('----------------------------')
if stderr is None:
    callgrind_pid = stdout.decode().split('\n')[0].split('==')[1]
    print(f'CPU profiling successful, with pid {callgrind_pid}')
else:
    raise ValgrindExecutionError()

# Perform Memory profiling with massif
print("Massif Memory Profiling")
arg_list = ['valgrind', '--tool=massif', massif_options, './' + executable_filename, program_arguments]
arg_list.remove('')
out = subprocess.Popen(arg_list, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
stdout, stderr = out.communicate()
print('-------Massif Output--------')
print(stdout.decode())
print('----------------------------')
if stderr is None:
    massif_pid = stdout.decode().split('\n')[0].split('==')[1]
    print(f'Memory profiling successful, with pid {massif_pid}')
else:
    raise ValgrindExecutionError()
