from tree_sitter import Parser
from tree_sitter_languages import get_language


class CodeParser:
    def __init__(self):
        self.languages = {
            "python": get_language("python"),
            "javascript": get_language("javascript"),
        }
        self.parser = Parser()

    def parse_file(self, file_path: str, language: str = "python"):
        """Parse a file with specified language"""
        with open(file_path, "rb") as f:
            code = f.read()
        return self.parse(code, language)

    def parse(self, code_bytes: bytes, language: str = "python"):
        """Parse raw code bytes with specified language"""
        self.parser.set_language(self.languages[language])
        return self.parser.parse(code_bytes)

    def parse_file_javascript(self, file_path: str, language: str = "javascript"):
        """Parse a file with specified language"""
        with open(file_path, "rb") as f:
            code = f.read()
        return self.parse(code, language)

    def parse_javascript(self, code_bytes: bytes, language: str = "javascript"):
        """Parse raw code bytes with specified language"""
        self.parser.set_language(self.languages[language])
        return self.parser.parse(code_bytes)
