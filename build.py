from tree_sitter import Language

Language.build_library("build/python.so", ["tree-sitter-python", "tree-sitter-javascript"])
