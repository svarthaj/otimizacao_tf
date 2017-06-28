import sys, os
from data_parser.data_parser import *
import time

import heapq
import random
from math import ceil

#-------------------------------------------------------------------------------
# general algorithms

def hill_climbing(solution, objective_function, neighbors, max_iterations):
    best_solution = solution
    current_best = objective_function(best_solution)
    previous_best = current_best - 1

    repetition_count = 0
    iteration = 0
    while repetition_count < 5:
        previous_best = current_best
        iteration += 1
        repetition_count += 1
        for neighbor in neighbors(best_solution):
            candidate = objective_function(neighbor)
    	    if candidate > current_best:
    	        best_solution = neighbor
                previous_best = current_best
                current_best = candidate
                repetition_count = 0

    return best_solution

def grasp(greedy_randomized_construction, local_search, neighbors, objective_function, max_iterations, alpha):
    best_solution = greedy_randomized_construction(alpha)
    for iteration in xrange(max_iterations):
        sys.stderr.write('iteration {}\n'.format(iteration))

        solution = greedy_randomized_construction(alpha)
        solution = local_search(solution, objective_function, neighbors, max_iterations)
        if objective_function(solution) > objective_function(best_solution):
            best_solution = solution

    return best_solution

#-------------------------------------------------------------------------------
# knapsack specific

def knapsack_weight(knapsack):
    w = 0
    for i in knapsack:
        w += weights[i]
    return w

def knapsack_profit(knapsack):
    p = 0
    for i in knapsack:
        p += profits[i]
    return p

def can_add(item, knapsack, remaining_space):
    if item in knapsack:
        return False

    if remaining_space - weights[item] < 0:
        return False

    if any([i in conflicts[item] for i in knapsack]):
        return False

    return True

def all_unique(x):
    seen = list()
    return not any(i in seen or seen.append(i) for i in x)

def neighboring_knapsacks_weight_2(knapsack, p):
    num_neighbors = max(1, int(len(knapsack)*p))

    neighbors_count = 0
    neighbors = []
    while neighbors_count < num_neighbors:
        item = random.sample(knapsack, 1)[0]

        neighbor = knapsack.copy()
        neighbor.remove(item)

        remaining_weight = capacity - knapsack_weight(neighbor)
        candidate_items = [i for i in items if can_add(i, neighbor, remaining_weight)]
        while candidate_items:
            new_item = random.choice(candidate_items)
            neighbor.add(new_item)
            remaining_weight -= weights[new_item]
            candidate_items = [i for i in items if can_add(i, neighbor, remaining_weight)]

        neighbors.append(neighbor)
        neighbors_count += 1

    return neighbors


def neigboring_knapsacks_hamming_1(knapsack):
    """
    Return a list of knapsacks neighboring the one given. Here, a neighbor is a
    knapsack built by either taking one item out or putting one item in. That
    is, an item 'flip'.
    """
    neighbors = []
    for item in items:
        neighbor = knapsack.copy()
        remain = capacity - knapsack_weight(neighbor)
        if item not in knapsack and can_add(item, neighbor, remain):
            neighbor.add(item)
            remain -= weights[item]
        elif item in knapsack:
            neighbor.remove(item)
        else: # cannot flip without becoming invalid
          continue

        neighbors.append(neighbor)

    return neighbors

def neighboring_knapsacks_weight_1(knapsack, p):
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
        remain = capacity - knapsack_weight(knapsack)
        candidate_items = [i for i in items if can_add(i, knapsack, remain) and i != excluded]

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
        if random.random() > p:
            continue
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

        remain = capacity - knapsack_weight(item_removed)
        valid_items = [i for i in items if can_add(i, item_removed, remain) and i != item]
        new_neighbors = [item_removed.copy() for i in valid_items]

        for i, n in zip(valid_items, new_neighbors):
            n.add(i)

        neighbors += new_neighbors

    return neighbors

def neighboring_knapsacks_switch_or_add_1(knapsack, p, q):
    """
    Return a list of knapsacks neighboring the one given. Here, a neighbor is a
    knapsack built by taking one item out of the original and putting another
    item in its place.
    """
    neighbors = []
    if random.random() > p:
        remain = capacity - knapsack_weight(knapsack)
        valid_items = [i for i in items if can_add(i, knapsack, remain)]
        if valid_items:
            new_neighbors = [knapsack.copy() for i in valid_items]
            for i, n in zip(valid_items, new_neighbors):
                n.add(i)

            neighbors += new_neighbors
            return neighbors

    for item in knapsack:
        if random.random() > q:
            continue

        item_removed = knapsack.copy()
        item_removed.remove(item)

        remain = capacity - knapsack_weight(item_removed)
        valid_items = [i for i in items if can_add(i, item_removed, remain) and i != item]
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
    incremental_profits = {i: float(profits[i])/weights[i] for i in items}
    remain = capacity
    while remain > 0:
        # build rcl
        candidate_items = [i for i in items if can_add(i, knapsack, remain)]
        if not candidate_items:
            break
        rcl = heapq.nlargest(int(alpha*len(candidate_items)) + 1, candidate_items, key=lambda i: incremental_profits[i])
        # select element from rcl and update knapsack
        new_item = random.choice(rcl)
        knapsack.add(new_item)
        remain -= weights[new_item]
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
# items: set( i:integer ) is the set of items by index
# weights: dict ( item: integer) dictionary key'd by item
# profits: dict ( item: integer ), similar to weights
# conflicts: dict ( item: set( integers ) )is a dcit key'd by items and each entry has a set of conflicting other items

num_items, capacity, items, weights, profits, conflicts = get_parameters(filename)

filename = sys.argv[1]
max_iterations = int(sys.argv[2])

start_time = time.time()
solution = grasp(greedy_randomized_knapsack_construction, hill_climbing, lambda x: neighboring_knapsacks_weight_2(x, 0.2), knapsack_profit, max_iterations, alpha)
print knapsack_profit(solution), time.time() - start_time

exit(0)
