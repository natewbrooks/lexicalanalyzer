from lexicalanalyzer import LexicalAnalyzer
from parser import SyntaxParser

import os

def analyze_file(filepath: str):
    la = LexicalAnalyzer(filepath=filepath)
    sp = SyntaxParser(la)
    print(f"Lexical+Syntax analysis on '{filepath}' complete.")

def analyze_directory(dirpath: str):
    for root, _, files in os.walk(dirpath):
        for name in files:
            print("Analyzing: ", name)
            filepath = os.path.join(root, name)
            analyze_file(filepath)

def parse_input_path() -> str | None:
    path = input("Enter a file or directory path: ").strip()
    if not path:
        return None
    if not os.path.exists(path):
        print("That path does not exist!")
        return None
    return path

def main():
    while True:
        path = parse_input_path()
        if not path:
            continue

        if os.path.isdir(path):
            analyze_directory(path)
        else:
            analyze_file(path)

main()
