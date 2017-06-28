def get_parameters(filename):
    input_file = open(filename, "r")
    lines = input_file.read().splitlines(1)
    n = 0
    c = 0

    items = set()
    weights = {}
    profits = {}
    conflicts = {}

    for line in lines:
        if "param n" in line:
            n = int(line.split()[-1].split(";")[0])
        elif "param c" in line:
            c = int(line.split()[-1].split(";")[0])
        elif "param" in line:
            for i in range(lines.index(line)+1, lines.index(line)+n+1):
                values = lines[i].split()
                if len(values) == 3:
                    it = int(values[0])
                    items.add(it)
                    profits[it] = int(values[1])
                    weights[it] = int(values[2])
        elif "set" in line:
            for i in range(lines.index(line)+1, len(lines)):
                values = lines[i].split()
                if len(values) == 2:
                    k1 = int(values[0])
                    k2 = int(values[1])
                    if k1 not in conflicts:
                        conflicts[k1] = set()
                        conflicts[k1].add(k2)
                    else:
                        conflicts[k1].add(k2)
                    if k2 not in conflicts:
                        conflicts[k2] = set()
                        conflicts[k2].add(k1)
                    else:
                        conflicts[k2].add(k1)

    return n, c, items, weights, profits, conflicts
