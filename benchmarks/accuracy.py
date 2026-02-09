# benchmarks/accuracy.py
correct = 0
total = len(test_cases)

for case in test_cases:
    if detect_quicksort(case["code"]) == case["expected"]:
        correct += 1

print(f"Accuracy: {correct/total:.2%}")
