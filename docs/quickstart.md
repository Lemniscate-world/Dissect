# Dissect Quickstart

## Basic Usage
```bash
# Detect algorithms in a file
dissect analyze --file my_code.py

# Generate visualization
dissect visualize --file my_code.py --output flowchart
```

## Supported Algorithms
| Algorithm       | Detection Scope          |
|-----------------|--------------------------|
| Quicksort       | Lomuto/Hoare variants    |
| BFS             | Queue-based traversal    |
| DFS             | Stack/recursive variants |
| Binary Search   | Iterative/recursive      |

## Visualization Categories
| Category  | Color     | Example Algorithms |
|-----------|-----------|---------------------|
| Sorting   | #FFEBEE   | Quicksort, Mergesort|
| Graph     | #E3F2FD   | BFS, DFS            |


## Why Nodes ?
A Node is a data structure that stores a value that can be of any data type and has a pointer to another node. The implementation of a Node class in a programming language such as Python, should have methods to get the value that is stored in the Node, to get the next node, and to set a link to the next node.

Data structures containing nodes have typically two bits of information stored in a node: data and link to next node.
