import sys, re
import collections


def get_parameters(filename):
    input_file = open(filename, "r")
    lines = input_file.read().splitlines(1)
    n = 0
    c = 0

    item = collections.namedtuple("item", ["i", "p", "w"])
    items = set()
    weights = {}
    profits = {}
    conflicts = {}

    exps = "(param|set)\s*(c|n|: V : p w|E)\s*:=\s*(\d*);*"
    for line in lines:
        m1 = re.match(exps, line)
        try:
            if m1.group(1) == "param":
                if m1.group(2) == "n":
                    n = int(m1.group(3))
                elif m1.group(2) == "c":
                    c = int(m1.group(3))
                elif m1.group(2) == ": V : p w":
                    for l in range(lines.index(line), lines.index(line)+n+1):
                        m2 = re.match("\s*(\d+)\s*(\d+)\s*(\d+)", lines[l])
                        try:
                            it = int(m2.group(1))
                            p = int(m2.group(2))
                            w = int(m2.group(3))
                            items.add(it)
                            weights[it] = w
                            profits[it] = p
                        except:
                            continue
            elif m1.group(1) == "set":
                for l in range(lines.index(line), len(lines)+1):
                    m2 = re.match("\s*(\d+)\s*(\d+)", lines[l])
                    try:
                        k1 = int(m2.group(1))
                        k2 = int(m2.group(2))
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
                    except:
                        continue
            else:
                pass
        except:
            continue
    
    return n, c, items, weights, profits, conflicts
