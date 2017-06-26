import sys
from data_parser.data_parser import *

if len(sys.argv) != 2:
    print "Usage $ python grasp.py [data_file]"
else:
    filename = sys.argv[1]

# n: integer is a number of items
# c: integer is maximum capacity of knapsack
# items: set( item(i:integer, p:integer, w:integer) ) is the set of items
# conflict: set( tuple(e1, e2) ) is a set of tuples for each item conflict

n, c, items, weights, profits, conflicts = get_parameters(filename)

print n, c
print items
print weights
print profits
print conflicts
