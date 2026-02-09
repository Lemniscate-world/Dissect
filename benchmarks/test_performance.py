# benchmarks/test_performance.py
import timeit


def benchmark_detection():
    setup = "from dissect.detectors.quicksort import detect_quicksort"
    stmt = "detect_quicksort(sample_node, sample_code)"
    return timeit.timeit(stmt, setup, number=1000)


print(f"Detection time: {benchmark_detection():.4f} sec/1000 runs")
