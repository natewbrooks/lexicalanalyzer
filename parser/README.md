## Syntax Parser

Created by Nate Brooks

---

### Overview

This project implements a **recursive-descent syntax parser** for the course language.  
It uses the existing `LexicalAnalyzer` to tokenize the input, then `SyntaxParser` to:

- Validate that the program conforms to the grammar (declarations, statements, expressions).
- Report the **first syntax error** with:
  - the unexpected token kind,
  - the line and character position, and
  - the set of expected token kinds.

When a file parses successfully, both lexical and syntax analysis complete without error.

---

### Environment

- **Language:** Python 3.13.5
- **Interpreter:** CPython, no external libraries
- **Editor:** Visual Studio Code
- **OS:** Arch Linux

No third-party dependencies or external modules are required.

---

### How to Run the Syntax Parser

1. Ensure Python 3 is installed and available on your `PATH`.

2. From the project root directory (where `main.py` lives), run:

   ```
   python main.py
   ```

3. When prompted: `Enter a file or directory path:`

   Enter either:
   - a **single source file path** (e.g. `examples/correct/print.txt`), or  
   - a **directory path** (e.g. `examples/correct`), in which case every file in that directory tree will be analyzed.

   Examples of valid input at the prompt:

   ```
   Enter a file or directory path: examples/correct/print.txt
   ```

   or

   ```
   Enter a file or directory path: examples/incorrect
   ```

4. For each file analyzed, the driver will construct a `LexicalAnalyzer` and `SyntaxParser` and, on success, print:

   ```
   Lexical and syntax analysis on '<filepath>' complete.
   ```

5. If a syntax error is detected, the parser will raise a `SyntaxError` similar to:

   ```
   SyntaxError: Bad symbol 'ID' at 9:4, expected (';') instead.
   ```

   where:
   - the **bad symbol** is the unexpected token kind,
   - the position is `line:column` in the source file, and
   - the **expected** list shows all token kinds that would have been valid at that point.

Execution stops on the first syntax error in each file. Files that parse without error will only show the completion message.