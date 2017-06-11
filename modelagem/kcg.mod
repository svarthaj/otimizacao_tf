param n;
/* number of items */

set V;
/* items */

set E within {0 .. n-1, 0 .. n-1};
/* set of tuples (e1, e2) where e1 and e2 are nodes on the graph representing conflicting items */

param c;
/* maximum capacity of knapsack */

param p{v in V};
/* profit for each item */

param w{v in V};
/* weight for each item */

var x{v in V}, binary;
/* variable indicating if a given item is included in the knapsack.
   - 1, if the item is included
   - 0, otherwise */

maximize profit: sum{v in V} x[v] * p[v];
/* profit function */ 

s.t. capacity: sum{v in V} x[v] * w[v] <= c;
/* maximum capacity constraint */

s.t. conflict{(e1, e2) in E}: x[e1] + x[e2] <= 1;
/* item conflict constraints. one for each tuple in E */

end;
