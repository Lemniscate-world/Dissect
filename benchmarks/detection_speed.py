import timeit


def benchmark_dfs_detection():
    setup = """
    from dissect.parser import CodeParser
    from dissect.detectors.dfs import detect_dfs
    code = b"def dfs(node):..."
    parser = CodeParser()
    tree = parser.parse(code)
    node = next(n for n in tree.root_node.children if n.type == 'function_definition')
    """

    time_per_call = timeit.timeit("detect_dfs(node, code)", setup=setup, number=1000) / 1000

    print(f"DFS detection latency: {time_per_call * 1e6:.2f} μs")
