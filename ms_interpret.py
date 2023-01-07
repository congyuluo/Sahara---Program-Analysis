import re
from errors import MassifInterpreterError


def interpret_massif_output(filename: str) -> dict:
    """
    Output format:
    name: [Allocated memory at each snapshot]
    """

    # Function to check for mistakes in interpreted input
    def check_snap(snap: []):
        primary_allocation_sum = sum([i[0] for i in snap[0]])
        function_allocation_sum = sum([i[0] for i in snap[1]])
        if primary_allocation_sum != function_allocation_sum:
            raise MassifInterpreterError()

    file1 = open(filename, 'r')
    snaps = []
    func_names = set()
    snap_count = -1
    while True:
        line = file1.readline()
        if not line:
            check_snap(snaps[-1])
            break
        line = line[:-1]

        # Increment snapshot count
        if re.fullmatch(r'^snapshot=\d+', line):
            # Check previous snapshot
            if snap_count != -1:
                check_snap(snaps[-1])

            snap_count += 1
            snaps.append([[], []])

        # If contains detail
        elif re.fullmatch(r'^ {0,1}\w\d:.+', line):

            if re.fullmatch(r'^\w\d: (\d+) .+', line):
                temp = re.search(r'^\w\d: (\d+) .+', line)
                snaps[-1][0].append(tuple([int(temp.groups()[0]), "Base allocation method"]))

            # Match function info
            elif re.fullmatch(r'^ {0,1}\w\d: (\d+) \S+ (\w+) \(.+\)', line):
                # Search for capture groups (allocation size and function name)
                temp = re.search(r'^ {0,1}\w\d: (\d+) \S+ (\w+) \(.+\)', line)
                snaps[-1][1].append([int(temp.groups()[0]), temp.groups()[1]])
                func_names.add(temp.groups()[1])

    # Close Massif out
    file1.close()

    # Prepare variables
    result = dict()
    result['total'] = []

    for func_name in func_names:
        result[func_name] = []

    # Reformat data
    for snap in snaps:
        appeared_funcs = set()
        result['total'].append(sum([i[0] for i in snap[0]]))
        for func in snap[1]:
            result[func[1]].append(func[0])
            appeared_funcs.add(func[1])
        for func in func_names:
            if func not in appeared_funcs:
                result[func].append(0)

    return result
