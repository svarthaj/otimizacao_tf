from sys import stderr

import random
from random import sample, choice
from heapq import nlargest

from data_parser.data_parser import *
import argparse

#-------------------------------------------------------------------------------
# general algorithms

def hill_climbing(solution, objective_function, neighbors, max_iterations, max_repetitions):
    """
    Return the best solution found by the Hill Climbing algorithm.

    solution: the starting solution
    objective_function: function that takes a solution and returns it's value
    neighbors: function takes a solution and returns it's neighbors
    max_iterations: maximum number of iterations
    max_repetitions: maximum number of iterations with the same best solution
    """
    best_solution = solution
    current_best = objective_function(best_solution)
    repetitions = 0
    iteration = 0
    while repetitions < max_repetitions and iteration < max_iterations:
        iteration += 1
        repetitions += 1
        for neighbor in neighbors(best_solution):
            candidate = objective_function(neighbor)
    	    if candidate > current_best:
    	        best_solution = neighbor
                current_best = candidate
                repetitions = 0

    return best_solution


def grasp(greedy_randomized_construction, local_search, objective_function, max_iterations, max_repetitions, alpha):
    """
    Return the best solution found by the GRASP algorithm.

    greedy_randomized_construction: function that returns a solution according
        to the GRASP algorithm
    local_search: function takes a solution and returns another after running a
        local search algorithm
    objective_function: function that takes a solution and returns it's value
    max_iterations: maximum number of iterations
    max_repetitions: maximum number of iterations with the same best solution
    alpha: the alpha parameter of the GRASP algorithm
    """
    best_solution = greedy_randomized_construction(alpha)
    repetitions = 0
    iteration = 0
    while repetitions < max_repetitions and iteration < max_iterations:
        stderr.write('\rGRASP iteration {}  '.format(iteration))
        repetitions += 1
        iteration += 1
        solution = greedy_randomized_construction(alpha)
        solution = local_search(solution)
        if objective_function(solution) > objective_function(best_solution):
            best_solution = solution
            repetitions = 0
    stderr.write('\n')

    return best_solution

#-------------------------------------------------------------------------------
# knapsack specific

def knapsack_weight(knapsack):
    """
    Return the weight of `knapsack`
    """
    return sum([weights[i] for i in knapsack])


def knapsack_profit(knapsack):
    """
    Return the profit of `knapsack`
    """
    return sum([profits[i] for i in knapsack])


def can_add(item, knapsack, remaining_weight):
    """
    Return True if `item` can be added to the `knapsack` with a remaining
    weight of `remaining_weight`, and False otherwise.
    """
    if item in knapsack:
        return False

    if remaining_weight - weights[item] < 0:
        return False

    if any([i in conflicts[item] for i in knapsack]):
        return False

    return True


def neighboring_knapsacks(knapsack, p):
    """
    Return a list of neighboring knapsacks to `knapsack`.

    A neighbor is generated by removing one item from `knapsack` and
    filling it up with new random items.

    `p` defines the maximum number of neighbors generated. The process
    described above is run for p*n different items in the knapsack, where
    n is the knapsack length.
    """
    num_neighbors = max(1, int(len(knapsack)*p))

    neighbors = []
    items_to_remove = sample(knapsack, num_neighbors)
    for item in items_to_remove:
        neighbor = knapsack.copy()
        neighbor.remove(item)

        remaining_weight = capacity - knapsack_weight(neighbor)
        candidate_items = [i for i in items if can_add(i, neighbor, remaining_weight)]
        while candidate_items:
            new_item = choice(candidate_items)
            neighbor.add(new_item)
            remaining_weight -= weights[new_item]
            candidate_items = [i for i in items if can_add(i, neighbor, remaining_weight)]

        neighbors.append(neighbor)

    return neighbors


def greedy_randomized_knapsack_construction(alpha):
    """
    Construct a new knapsack using the greedy randomized construction algorithm.
    """
    knapsack = set()
    remain = capacity
    while remain > 0:
        # build rcl
        candidate_items = [i for i in items if can_add(i, knapsack, remain)]
        if not candidate_items:
            break
        rcl = nlargest(int(alpha*len(candidate_items)) + 1, candidate_items, key=lambda i: incremental_profits[i])
        # select element from rcl and update knapsack
        new_item = choice(rcl)
        knapsack.add(new_item)
        remain -= weights[new_item]
        # reevaluate incremental_profit (not needed here)

    return knapsack


#-------------------------------------------------------------------------------
# main

def parse_args():
    parser = argparse.ArgumentParser(description='0/1 Knapsack with conflicts GRASP optimization program.')
    parser.add_argument('instance', type=str, help='The .dat instance file.')
    parser.add_argument('--alpha', type=float, help='Alpha parameter of the GRASP algorithm.', default=5)
    parser.add_argument('--seed', type=int, help='Seed for the random module.', default=0)
    parser.add_argument('--giter', type=int, help='Max iterations for GRASP.', default=10)
    parser.add_argument('--grep', type=int, help='Max iterations with repeated best solution for GRASP.', default=5)
    parser.add_argument('--lsrep', type=int, help='Max iterations with repeated best solution for the local search.', default=100)
    parser.add_argument('--lsiter', type=int, help='Max iterations for the local search.', default=5)
    parser.add_argument('--pneigh', type=float, help='Parameter p for neighbors generation. A maximum of int(p*len(solution)) of neighbors will be consider for each solution.', default=0.2)
    parser.add_argument('--fsol', type=str, help='File to print solution.', default='/dev/null')

    args = parser.parse_args()

    global filename
    global max_grasp_iterations
    global max_grasp_repetitions
    global max_local_search_iterations
    global max_local_search_repetitions
    global neighbors_p
    global alpha
    global seed
    global solution_file
    filename = args.instance
    max_grasp_iterations = args.giter
    max_grasp_repetitions = args.grep
    max_local_search_iterations = args.lsiter
    max_local_search_repetitions = args.lsrep
    neighbors_p = args.pneigh
    alpha = args.alpha
    seed = args.seed
    solution_file = open(args.fsol, 'w')
    stderr.write('\nArguments:\n')
    for arg in vars(args):
        stderr.write('\t' + str(arg) + ': ' + str(getattr(args, arg)) + '\n')
    stderr.write('\n')


parse_args()

# num_items: integer is a number of items
# capacity: integer is maximum capacity of knapsack
# items: set( i:integer ) is the set of items by index
# weights: dict ( item: integer) dictionary key'd by item
# profits: dict ( item: integer ), similar to weights
# conflicts: dict ( item: set( integers ) )is a dcit key'd by items and each entry has a set of conflicting other items
num_items, capacity, items, weights, profits, conflicts = get_parameters(filename)

# incremental_profits to be used in the greedy randomized construction
incremental_profits = {i: float(profits[i])/weights[i] for i in items}

random.seed(seed)

# apply partial arguments to the neighbors function
neighbors = lambda knapsack: neighboring_knapsacks(knapsack, neighbors_p)

# apply partial arguments to hill_climbing
local_search = lambda solution: hill_climbing(solution,
                                              knapsack_profit,
                                              neighbors,
                                              max_local_search_iterations,
                                              max_local_search_repetitions)

# find best solution
solution = grasp(greedy_randomized_knapsack_construction,
                 local_search,
                 knapsack_profit,
                 max_grasp_iterations,
                 max_grasp_repetitions,
                 alpha)

for i in solution:
    solution_file.write(str(i) + '\n')
print knapsack_profit(solution)
solution_file.close()
