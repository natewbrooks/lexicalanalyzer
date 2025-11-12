from lexicalanalyzer import LexicalAnalyzer
from parser import SyntaxParser

def main():
    while True:
        filepath = parse_input_file()
        if not filepath:
            continue

        la = LexicalAnalyzer(filepath=filepath)
        sp = SyntaxParser(la)

        # la.next()
        # print(la.lexemes[-1]) # print(f"{la.line_num}:{la.position()}:'{la.kind()}' {la.value()}")
        # while la.kind() != 'end-of-text':
        #     la.next()
        #     print(la.lexemes[-1]) # print(f"{la.line_num}:{la.position()}:'{la.kind()}' {la.value()}")

        print(f"Lexical+Syntax analysis on '{filepath}' complete.")

# Loop through and take user input to assign the lexical analyzer a filepath
def parse_input_file():
    filepath = input("Enter the language file path: ")
    try:
        with open(filepath, 'r') as f:
            return filepath
    except:
        print("That filepath does not exist!")
        return None

main()