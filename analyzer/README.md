## Lexical Analyzer

Created by Nate Brooks

---

### Programming Language
- **Language:** Python
- **Development Version:** Python 3.13.5

### Interpreter

This project runs on the Python interpreter. No external libraries were used.


### Development Environment
- **Editor:** Visual Studio Code
- **Operating System:** Arch Linux
- **No dependencies or external modules**

### Execution Instructions
1. Ensure [Python3](https://www.python.org/downloads/) is installed and added to your system PATH
2. Open a terminal in the project directory and run the command `python main.py`
3. When the program prompts `Enter the language file path:`
provide the relative filepath to the source program file to be analyzed. For example, `text/tricky.txt`
4. The analyzer will then process the file and print each lexeme in the format `<line_num>:<char_pos>:'<token_type>' <value>`
5. When the end of the file is reached, or an invalid character is processed, the analyzer's execution will stop.
    - You will know the program ran successfully if you see the message `Lexical analysis on '{filepath}' complete`. 
        - Otherwise, the program will raise an error (e.g. `ValueError: Invalid symbol '!' at line 6, char 13`)

### Program Information
- Each lexeme is formatted as:
    1. line_number: the line of the lexeme in the source file
    2. char_pos: the start position of the lexeme in the source file relative to its line number
    3. token_type: the 'kind' of the lexeme in the source file
    4. value: displayed only for lexemes with kind ('ID' or 'NUM')

- The analyzer reads and validates each character:
    - It recognizes:
        - **Reserved keywords:** "program", "true", "false", "if", "then", "else", "while", "do", "end", "print", "int", "bool", "and", "or", "not", "mod"
        - **Reserved symbols:** "=", ":=", ";", ":", "<", ">", "*", "<=", ">=", "!=", "+", "-", "/", "(", ")"
    - Comments begin with `//` and continue to the end of the line
    - Invalid characters trigger a `ValueError` with the line and character position

