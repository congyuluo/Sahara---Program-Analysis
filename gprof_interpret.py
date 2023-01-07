import re
from errors import GProfInterpreterError

match_regex = r'^ +(\d+.\d+) +(\d+.\d+) +(\d+.\d+) +(\d+) +(\d+.\d+) +(\d+.\d+) +(\w+)$'


def interpret_gprof_result(x: str) -> dict:
    """
    Output format:
    name : [%time, cumulative seconds, self seconds, calls, self Ts/call, total Ts/call]
    """
    result = dict()
    # Iterate over every function
    for line in x.split('\n'):
        if re.fullmatch(match_regex, line):
            temp = re.search(match_regex, line)

            if len(temp.groups()) != 7:
                raise GProfInterpreterError()

            result[temp.groups()[6]] = temp.groups()[:-1]
    return result
