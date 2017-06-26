import sys
from data_parser.data_parser import *

import heapq
import random
from math import ceil

#-------------------------------------------------------------------------------
# general algorithms

def hill_climbing(solution, objective_function, neighbors):
    best_solution = solution
    curr = objective_function(best_solution)
    prev = curr - 1

    while prev != curr:
        prev = curr
        for neighbor in neighbors(best_solution):
    	    if objective_function(neighbor) > objective_function(best_solution):
                curr = objective_function(neighbor)
    	        best_solution = neighbor

    return best_solution

def grasp(greedy_randomized_construction, local_search, neighbors, objective_function, max_iterations, alpha):
    best_solution = greedy_randomized_construction(alpha)
    print 'new best: ' + str(objective_function(best_solution))
    for iteration in xrange(max_iterations):
        solution = greedy_randomized_construction(alpha)
        solution = local_search(solution, objective_function, neighbors)
        if objective_function(solution) > objective_function(best_solution):
            best_solution = solution
            print 'new best: ' + str(objective_function(best_solution))

    return best_solution

#-------------------------------------------------------------------------------
# knapsack specific

def knapsack_weight(knapsack):
    return sum([weights[i] for i in knapsack])

def knapsack_profit(knapsack):
    return sum([profits[i] for i in knapsack])

def can_add(item, knapsack):
    if item in knapsack:
        return False

    if knapsack_weight(knapsack) + weights[item] > capacity:
        return False

    if any([i in conflicts_dict[item] for i in knapsack]):
        return False

    return True

def all_unique(x):
    seen = list()
    return not any(i in seen or seen.append(i) for i in x)

def neigboring_knapsacks_hamming_1(knapsack):
    """
    Return a list of knapsacks neighboring the one given. Here, a neighbor is a
    knapsack built by either taking one item out or putting one item in. That
    is, an item 'flip'.
    """
    neighbors = []
    for item in all_items:
        neighbor = knapsack.copy()
        if item not in knapsack and can_add(item, neighbor):
            neighbor.add(item)
        elif item in knapsack:
            neighbor.remove(item)
        else: # cannot flip without becoming invalid
          continue

        neighbors.append(neighbor)

    return neighbors

def neighboring_knapsacks_weight_1(knapsack):
    """
    Return a list of knapsacks neighboring the one given. Here, a neighbor is a
    knapsack built by taking one item out of the original and filling it up
    again as much as possible.
    """
    def fill_from(knapsack, excluded):
        """
        Return a list with all possible ways to fill the knapsack by adding zero
        or more items to the one given. Exclude the item given by the second
        argument.
        """
        full_knapsacks = []
        candidate_items = [i for i in all_items if can_add(i, knapsack) and i != excluded]

        if candidate_items != []:
            for item in candidate_items:
                new_knapsack = knapsack.copy()
                new_knapsack.add(item)
                full_knapsacks += fill_from(new_knapsack, excluded)
        else: # can't add anything more
            full_knapsacks.append(knapsack)

        unique = []
        for k in full_knapsacks:
            if k not in unique:
                unique.append(k)

        return unique

    neighbors = []
    for item in knapsack:
        item_removed = knapsack.copy()
        item_removed.remove(item)
        neighbors += fill_from(item_removed, item)

    return neighbors

def neighboring_knapsacks_switch_1(knapsack):
    """
    Return a list of knapsacks neighboring the one given. Here, a neighbor is a
    knapsack built by taking one item out of the original and putting another
    item in its place.
    """
    neighbors = []
    for item in knapsack:
        item_removed = knapsack.copy()
        item_removed.remove(item)

        valid_items = [i for i in all_items if can_add(i, item_removed) and i != item]
        new_neighbors = [item_removed.copy() for i in valid_items]

        for i, n in zip(valid_items, new_neighbors):
            n.add(i)

        neighbors += new_neighbors

    return neighbors

def greedy_randomized_knapsack_construction(alpha):
    """
    Construct a new knapsack using the greedy randomized construction algorithm.
    """
    knapsack = set()
    incremental_profits = {i: float(weights[i])/profits[i] for i in all_items}
    while knapsack_weight(knapsack) <= capacity:
        # build rcl
        candidate_items = [i for i in all_items if can_add(i, knapsack)]
        if not candidate_items:
            break
        rcl = heapq.nlargest(int(alpha*len(candidate_items)) + 1, candidate_items, key=lambda i: incremental_profits[i])
        # select element from rcl and update knapsack
        knapsack.add(random.choice(rcl))
        # reevaluate incremental_profit (not needed here)

    return knapsack

#-------------------------------------------------------------------------------
# main

if len(sys.argv) != 5:
    print "Usage: python grasp.py <data_file> <max iterations> <alpha> <seed>"
    exit(1)

filename = sys.argv[1]
max_iterations = int(sys.argv[2])
alpha = float(sys.argv[3])
seed = int(sys.argv[4])

random.seed(seed)

# num_items: integer is a number of items
# capacity: integer is maximum capacity of knapsack
# items: set( item(i:integer, p:integer, w:integer) ) is the set of items
# conflict: set( tuple(e1:integer, e2:integer) ) is a set of tuples for each item conflict

num_items, capacity, items, conflicts = get_parameters(filename)

all_items = [i.i for i in items]
weights = {i.i: i.w for i in items}
profits = {i.i: i.p for i in items}

conflicts_dict = {}
conflicts_dict.update({i: set() for i in all_items})
for i, j in conflicts:
    conflicts_dict[i].add(j)
    conflicts_dict[j].add(i)

#print num_items, capacity, len(items), conflicts_dict
assert all([j in conflicts_dict[i] for i, j in conflicts])
assert all([i in conflicts_dict[j] for i, j in conflicts])

filename = sys.argv[1]
max_iterations = int(sys.argv[2])

solution = grasp(greedy_randomized_knapsack_construction, hill_climbing, neighboring_knapsacks_weight_1, knapsack_profit, max_iterations, alpha)
print '-'*10 + ' final solution:'
print 'set:', solution
print 'profit:', knapsack_profit(solution)
print 'weight:', knapsack_weight(solution)

exit(0)
