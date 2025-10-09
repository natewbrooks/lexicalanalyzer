class LexicalAnalyzer:
    def __init__(self, filepath):
        # GIVEN
        self.filepath: str = filepath
        # RESERVED VALUES
        self.reserved: dict = {
            "keywords": ["program", "true", "false", "if", "then", "else", "while", "do", "end", "print", "int", "bool", "and", "or", "not", "mod"],
            "symbols": [":=", ";", ":", "<", ">", "*", "<=", ">=", "!=", "+", "-", "/", "(", ")"]
        }
        # LOOKAHEAD
        self.lookahead: str = "" # Value of lookahead char
        self.pos: int = -1 # Position of lookahead
        self.line_num: int = 1 # Line number of the lookahead
        self.pos_offset: int = 0
        self.comment_flag: bool = False # Should we ignore the remainder of the line?
        self.eof_emitted: bool = False # Has EOF token been emitted?
        # LEXEMES
        self.lexemes = []
        
        # Operator helpers
        self._two_char_ops = {":=", "<=", ">=", "!="}
        self._sym_starters = set(":<>=!;*+-/()")

    def _peek(self, f):
        cur = f.tell()
        ch = f.read(1)
        f.seek(cur)
        return ch

    # 1-index columns when computed 0
    def _col(self, abs_start):
        col = abs_start - self.pos_offset
        return 1 if col == 0 else col

    def next(self):
        with open(self.filepath, 'r') as f:
            # Read one char. If it is not a space, add it to the current lexeme
            # if the lexeme is new, set its start position to the current position
            # keep going until the char is a whitespace (lexeme finished) or char is 
            # not approved (invalid)
            #
            # If the char is a reserved keyword/symbol, we need to handle that as it occurs
            
            if self.eof_emitted:
                return
            
            self.pos += 1 # increment to move past current lexeme
            start_pos = -1 # reset start position for current lexeme
            lexeme = "" # reset lexeme
            numeric_mode = False  # Track “starts with digit” for 2int/5else
            
            f.seek(self.pos)
            
            while True:
                self.lookahead = f.read(1)

                # End-of-file
                if self.lookahead == "":
                    if lexeme and not self.comment_flag:
                        if (len(self.lexemes) == 0): 
                            start_pos += 1  # The first lexeme should start at char 1
                        self.lexemes.append(Lexeme(lexeme, self._col(start_pos), self.line_num, reserved=self.reserved))
                    if not self.eof_emitted:
                        # place EOF at col 1 to avoid 0
                        self.lexemes.append(Lexeme("end-of-text", 1, self.line_num, reserved=self.reserved))
                        self.eof_emitted = True
                    break
                
                # Invalid character check
                if not self.validate(self.lookahead):
                    raise ValueError(f"Invalid character '{self.lookahead}' at line {self.line_num}, col {self.pos - self.pos_offset}")

                # Comment mode
                if self.comment_flag:
                    if self.lookahead == "\n":
                        self.line_num += 1
                        self.pos_offset = self.pos
                        self.comment_flag = False
                    self.pos += 1
                    continue
                
                # Ignore whitespace
                if self.lookahead.isspace() and lexeme.strip() == "":
                    if self.lookahead == "\n":
                        self.line_num += 1
                        self.pos_offset = self.pos
                    self.pos += 1
                    continue
                
                # If theres a comment
                if self.lookahead == "/" and self._peek(f) == "/":
                    self.comment_flag = True
                    f.read(1)  # consume second slash
                    self.pos += 2
                    continue
                
                # If it’s a symbol (may be two-character)
                if self.lookahead in self._sym_starters:
                    # Emit any pending lexeme first
                    if lexeme:
                        if (len(self.lexemes) == 0): start_pos += 1
                        self.lexemes.append(Lexeme(lexeme, self._col(start_pos), self.line_num, reserved=self.reserved))
                        return

                    nxt = self._peek(f)
                    candidate = self.lookahead + (nxt or "")
                    if candidate in self._two_char_ops:
                        f.read(1)
                        self.pos += 1  # consumed second char of two-char op
                        self.lexemes.append(Lexeme(candidate, self._col(self.pos - 1), self.line_num, reserved=self.reserved))
                        return
                    else:
                        self.lexemes.append(Lexeme(self.lookahead, self._col(self.pos), self.line_num, reserved=self.reserved))
                        return 
                
                # When the lexeme is finished
                elif self.lookahead.isspace():
                    if not self.comment_flag:
                        if (len(self.lexemes) == 0): start_pos += 1 # The first lexeme should start at char 1 
                        self.lexemes.append(Lexeme(lexeme, self._col(start_pos), self.line_num, reserved=self.reserved))
                    
                    # Track if there was a new line
                    if self.lookahead == "\n":
                        self.line_num += 1
                        self.pos_offset = self.pos
                        self.comment_flag = False
                    
                    break
                
                # Add current lookahead to the lexeme being built
                if start_pos == -1:
                    start_pos = self.pos
                    numeric_mode = self.lookahead.isdigit()  # Mark numeric start
                lexeme += self.lookahead
                self.pos += 1         

                # Peek for lexeme boundary
                nxt = self._peek(f)

                # If token started numeric and next is a letter/underscore, split the lexemes (2int -> '2' then 'int')
                if numeric_mode and (nxt.isalpha() or nxt == "_"):
                    if (len(self.lexemes) == 0): start_pos += 1
                    self.lexemes.append(Lexeme(lexeme, self._col(start_pos), self.line_num, reserved=self.reserved))
                    self.pos -= 1  # keep next() aligned on the first letter
                    break

                if nxt == "" or nxt.isspace() or (nxt in self._sym_starters) or (nxt == "/" and self._peek(f) == "/"):
                    if (len(self.lexemes) == 0): start_pos += 1
                    self.lexemes.append(Lexeme(lexeme, self._col(start_pos), self.line_num, reserved=self.reserved))
                    self.pos -= 1  # keep next() aligned on the boundary char
                    break

    def kind(self):
        return self.lexemes[-1].kind if self.lexemes else ""

    def value(self):
        return self.lexemes[-1].value if self.lexemes and self.lexemes[-1].kind in ("ID", "NUM") else ""

    def position(self):
        return self.lexemes[-1].pos if self.lexemes else ""
    
    def validate(self, ch):
        # Allow letters, digits, underscore, whitespace, and valid symbols
        return ch.isalnum() or ch == "_" or ch.isspace() or ch in self._sym_starters
        
    def __str__(self):
        return "file: " + self.filepath
        

class Lexeme:
    def __init__(self, value, pos, line_num, reserved):
        # RESERVED
        self.__reserved = reserved
        # Info
        self.value: str = value
        self.kind: str = ""
        # Position
        self.pos: int = pos # start position
        self.line_num: int = line_num
        self.validate() # check the kind or return error
        
    def validate(self):
        # Number
        if self.value.isdigit():
            self.kind = "NUM"
            self.value = int(self.value)
        # Keyword
        elif self.value in self.__reserved["keywords"]:
            self.kind = self.value
            self.value = ""
        # Symbol
        elif self.value in self.__reserved["symbols"]:
            self.kind = self.value
            self.value = ""
        # End of file
        elif self.value == "end-of-text":
            self.kind = "end-of-text"
            self.value = ""
        else:
            self.kind = "ID"
    
    def __str__(self):
        return f"{self.line_num}:{self.pos}:'{self.kind}' {self.value if (self.kind == 'ID' or self.kind == 'NUM') else ''}"


def main():
    while True:
        filepath = parse_input_file()
        if not filepath:
            continue

        a = LexicalAnalyzer(filepath=filepath)

        a.next()
        print(f"{a.line_num}:{a.position()}:'{a.kind()}' {a.value()}")
        while a.kind() != 'end-of-text':
            a.next()
            print(f"{a.line_num}:{a.position()}:'{a.kind()}' {a.value()}")

        print(f"Lexical analysis on '{filepath}' complete.")


def parse_input_file():
    filepath = input("Enter the language file path: ")
    try:
        with open(filepath, 'r') as f:
            return filepath
    except:
        print("That filepath does not exist!")
        return None


main()
