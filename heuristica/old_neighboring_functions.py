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

