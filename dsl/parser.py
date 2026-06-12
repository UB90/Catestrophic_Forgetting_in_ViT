from lark import Lark
from pathlib import Path

class PreprocessingParser:
    def __init__(self, grammar_path=None):
        if grammar_path is None:
            grammar_path = Path(__file__).parent / "preprocessing.lark"
        with open(grammar_path, "r") as f:
            grammar = f.read()
        self.parser = Lark(grammar, parser="lalr", start="start")

    def parse(self, text: str):
        return self.parser.parse(text)