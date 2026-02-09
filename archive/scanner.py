import os
from pathlib import Path

from .detectors.bfs import detect_bfs
from .detectors.binary_search import detect_binary_search
from .detectors.dfs import detect_dfs
from .detectors.mergesort import detect_mergesort
from .detectors.quicksort import detect_quicksort
from .parser import CodeParser


class AlgorithmScanner:
    def __init__(self):
        self.parser = CodeParser()
        self.supported_extensions = {".py", ".js", ".java"}
        self.ignore_dirs = {
            ".git",
            "venv",
            "__pycache__",
            "node_modules",
            ".idea",
            ".vscode",
            "build",
            "dist",
        }

    def scan_directory(self, root_path):
        inventory = {
            "meta": {"root": str(root_path), "total_files": 0, "algorithms_found": 0},
            "files": [],
        }

        for root, dirs, files in os.walk(root_path):
            # Prune ignored directories
            dirs[:] = [d for d in dirs if d not in self.ignore_dirs]

            for file in files:
                file_path = Path(root) / file
                if file_path.suffix in self.supported_extensions:
                    file_result = self.analyze_file(file_path)
                    if file_result and file_result["functions"]:
                        inventory["files"].append(file_result)
                        inventory["meta"]["algorithms_found"] += sum(
                            len(f["algorithms"]) for f in file_result["functions"]
                        )
                    inventory["meta"]["total_files"] += 1

        return inventory

    def analyze_file(self, file_path):
        ext_map = {".py": "python", ".js": "javascript", ".java": "java"}
        language = ext_map.get(file_path.suffix, "python")

        try:
            tree = self.parser.parse_file(str(file_path), language=language)
            with open(file_path, "rb") as f:
                code_bytes = f.read()
        except Exception:
            # print(f"Error parsing {file_path}: {e}") # Reduce noise
            return None

        file_data = {"path": str(file_path), "functions": []}

        # Find all function definitions (simplified traversal)
        # Note: Ideally this should be language-agnostic node type checking
        # For now relying on tree-sitter standard naming common in supported langs
        cursor = tree.walk()

        def traverse(node):
            if node.type == "function_definition" or node.type == "method_declaration":
                self._analyze_function_node(node, code_bytes, file_data)

            for child in node.children:
                traverse(child)

        traverse(tree.root_node)

        return file_data

    def _analyze_function_node(self, node, code_bytes, file_data):
        try:
            func_name = node.child_by_field_name("name").text.decode("utf-8")
        except:
            func_name = "anonymous"

        function_entry = {"name": func_name, "line": node.start_point[0] + 1, "algorithms": []}

        # Run Detectors
        # TODO: Refactor into a unified detector registry
        detectors = [
            ("Quicksort", detect_quicksort),
            ("BFS", detect_bfs),
            ("DFS", detect_dfs),
            ("Mergesort", detect_mergesort),
            ("BinarySearch", detect_binary_search),
        ]

        for alg_name, detector in detectors:
            try:
                result = detector(node, code_bytes)
                # Check for various success keys (legacy vs new)
                is_detected = result.get(f"is_{alg_name.lower().replace(' ', '_')}") or result.get(
                    f"is_{alg_name.lower()}"
                )

                if is_detected:
                    algo_data = {
                        "type": alg_name,
                        "confidence": result.get("confidence", 0),
                        "complexity": result.get("complexity", "Unknown"),
                        "category": result.get("category", "alg"),  # Fallback
                    }
                    function_entry["algorithms"].append(algo_data)
            except Exception:
                # Detector failure shouldn't crash scan
                pass

        if function_entry["algorithms"]:
            file_data["functions"].append(function_entry)
