int: n;                     % number of objects
set of int: OBJ = 1..n;
array[OBJ] of int: profit;  % the profit of each object
array[OBJ] of int: size;    % the size of each object
int: capacity;              % the capacity of the knapsack

var set of OBJ: x;
constraint sum(i in x)(size[i]) <= capacity;

var int: obj = sum(i in x)(profit[i]);
solve maximize obj;

output [
    "knapsack = ", show(x), "\n",
    "objective = ", show(obj)
];
