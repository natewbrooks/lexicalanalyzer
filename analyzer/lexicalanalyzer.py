class LexicalAnalyzer:
    def __init__(self, filepath):
        self.filepath: str = filepath
        # RESERVED VALUES
        self.reserved: dict = {
            "keywords": ["program", "true", "false", "if", "then", "else", "while", "do", "end", "print", "int", "bool", "and", "or", "not", "mod"],
            "symbols": ["=", ":=", ";", ",", ".", ":", "<", ">", "*", ">=", "=<", "!=", "+", "-", "/", "(", ")"]
        }
        # OPERATOR HELPERS
        self._two_char_ops = {":=", ">=", "=<", "!="}
        self._sym_starters = set(":<>=!;.,*+-/()")
        # LOOKAHEAD
        self.lookahead: str = "" # Value of lookahead char
        self.pos: int = -1 # Position of lookahead
        self.line_num: int = 1 # Line number of the lookahead
        self.pos_offset: int = 0
        self.comment_flag: bool = False # Should we ignore the remainder of the line?
        self.eof_emitted: bool = False # Has EOF token been emitted?
        # LEXEMES
        self.lexemes = []
        
    # Returns the last appended lexeme object
    def last(self):
        return self.lexemes[-1] if self.lexemes else None

    # Returns the character infront of the the current lookahead character in the file. 
    # Gets the current position in the file, reads the next char, returns to the previous (current) lookahead location,
    # and then returns the next character
    def _peek(self, f):
        cur = f.tell()
        ch = f.read(1)
        f.seek(cur)
        return ch

    # Return the char position in the current line. Uses a wrap-around value of the previous lines to
    # calculate the char position relative to the current line. 1-index pos when 0 is computed
    def _char_pos(self, abs_start):
        char_pos = abs_start - self.pos_offset
        return 1 if char_pos == 0 else char_pos

    # Read chars to build a lexeme and finalize it when a boundary char is hit (e.g. whitespace, symbol, EOF, comment)
    # or, raise an error if the char is not in the approved language (invalid)
    def next(self):
        with open(self.filepath, 'r') as f:
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
                    # If we have a lexeme and that lexeme wasn't a comment, append it
                    if lexeme and not self.comment_flag:
                        if (len(self.lexemes) == 0): 
                            start_pos += 1  # The first lexeme should start at char 1
                        self.lexemes.append(Lexeme(lexeme, self._char_pos(start_pos), self.line_num, reserved=self.reserved))
                    if not self.eof_emitted:
                        # place EOF at col 1 to avoid 0
                        self.lexemes.append(Lexeme("end-of-text", 1, self.line_num, reserved=self.reserved))
                        self.eof_emitted = True
                    break
                
                # Invalid character check
                if not self.validate(self.lookahead) and not self.comment_flag:
                    raise ValueError(f"Invalid character '{self.lookahead}' at line {self.line_num}, char {self.pos - self.pos_offset}")

                # Handle comment flag being on by skipping the current line
                if self.comment_flag:
                    if self.lookahead == "\n":
                        self.line_num += 1
                        self.pos_offset = self.pos
                        self.comment_flag = False
                    self.pos += 1
                    continue
                
                # Ignore all whitespace
                if self.lookahead.isspace() and lexeme.strip() == "":
                    if self.lookahead == "\n":
                        self.line_num += 1
                        self.pos_offset = self.pos
                    self.pos += 1
                    continue
                
                # If theres a comment, denoted by '//', trigger comment flag
                if self.lookahead == "/" and self._peek(f) == "/":
                    self.comment_flag = True
                    f.read(1)  # consume second slash
                    self.pos += 2
                    continue
                
                # If lookahead char is a recognized symbol (can be two-character)
                if self.lookahead in self._sym_starters:
                    # Finalize any unfinished lexeme before processing the next symbol
                    if lexeme:
                        if (len(self.lexemes) == 0): start_pos += 1
                        self.lexemes.append(Lexeme(lexeme, self._char_pos(start_pos), self.line_num, reserved=self.reserved))
                        return

                    # Check the char after the lookahead to see if it matches a reserved symbol
                    nxt = self._peek(f)
                    # Concatenate current lookahead and the future char to test if its a valid symbol
                    candidate = self.lookahead + (nxt or "")

                    # Prefer longest matching symbol (two-char ops)
                    if candidate in self._two_char_ops:
                        # If candidate is valid, file pos++ so we don't reuse the _peek'd char again
                        f.read(1)
                        self.pos += 1 
                        self.lexemes.append(Lexeme(candidate, self._char_pos(self.pos - 1), self.line_num, reserved=self.reserved))
                        return

                    # Otherwise, only allow the single char if it's an allowed symbol in the grammar (e.g. last '=' in ':==')
                    if self.lookahead in self.reserved["symbols"]:
                        self.lexemes.append(Lexeme(self.lookahead, self._char_pos(self.pos), self.line_num, reserved=self.reserved))
                        return

                    # If it's a starter symbol (e.g. '!' in '!=') but not a declared symbol (e.g. lone '!'), it's invalid
                    raise ValueError(f"Invalid symbol '{self.lookahead}' at line {self.line_num}, char {self.pos - self.pos_offset + 1}")
                
                # When the lexeme is finished and it wasnt commented out, append it
                elif self.lookahead.isspace():
                    if not self.comment_flag:
                        if (len(self.lexemes) == 0): start_pos += 1 # The first lexeme should start at char pos 1 
                        self.lexemes.append(Lexeme(lexeme, self._char_pos(start_pos), self.line_num, reserved=self.reserved))
                    
                    # Track if there was a new line introduced, set the new position offset
                    # for future lines' char position
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

                # Peek future char for lexeme boundary
                nxt = self._peek(f)

                # If token started numeric and next char is a letter/underscore, split the lexemes (2int -> '2' then 'int')
                if numeric_mode and (nxt.isalpha() or nxt == "_"):
                    if (len(self.lexemes) == 0): start_pos += 1
                    self.lexemes.append(Lexeme(lexeme, self._char_pos(start_pos), self.line_num, reserved=self.reserved))
                    self.pos -= 1  # keep next() aligned on the first letter
                    break

                # Finalize current token if next char ends it (whitespace, symbol, comment, or EOF)
                if nxt == "" or nxt.isspace() or (nxt in self._sym_starters) or (nxt == "/" and self._peek(f) == "/"):
                    if (len(self.lexemes) == 0): start_pos += 1
                    self.lexemes.append(Lexeme(lexeme, self._char_pos(start_pos), self.line_num, reserved=self.reserved))
                    self.pos -= 1  # keep next() aligned on the boundary char
                    break

    # Return the kind of last appended lexeme
    def kind(self):
        return self.lexemes[-1].kind if self.lexemes else ""

    # Return the value of last appended lexeme (only if it is an ID or NUM)
    def value(self):
        return self.lexemes[-1].value if self.lexemes and self.lexemes[-1].kind in ("ID", "NUM") else ""

    # Return the postiion of the last appended lexeme
    def position(self):
        return self.lexemes[-1].pos if self.lexemes else ""
    
    # Validate that character belongs to allowed language alphabet (letters, digits, underscores, symbols, or whitespace)
    def validate(self, ch):
        return ch.isalnum() or ch == "_" or ch.isspace() or ch in self._sym_starters
    
    # Ensures print(obj) returns the filepath
    def __str__(self):
        return "file: " + self.filepath
        

class Lexeme:
    def __init__(self, value, pos, line_num, reserved):
        # RESERVED
        # Passed from lexical analyzer, lexemes don't define what keywords are reserved, the machine does
        self.__reserved = reserved
        # INFO
        self.value: str = value # By default set the value to the string value passed in
        self.kind: str = ""
        # POSITION
        self.pos: int = pos # start position of the lexeme
        self.line_num: int = line_num # line number of the lexeme
        self.validate() # check the kind of the lexeme
        
    # Given the initialized lexeme value, determine and assign the kind of the lexeme 
    def validate(self):
        # Numbers
        if self.value.isdigit():
            self.kind = "NUM"
            self.value = int(self.value) # Convert the string to an int (e.g. '19' to 19)
        # Keywords
        elif self.value in self.__reserved["keywords"]:
            self.kind = self.value
            self.value = ""
        # Symbols
        elif self.value in self.__reserved["symbols"]:
            self.kind = self.value
            self.value = ""
        # End of file
        elif self.value == "end-of-text":
            self.kind = "end-of-text"
            self.value = ""
        # If nothing else, it's an ID
        else:
            self.kind = "ID"
            # Value doesn't need to change because its already the string value
    
    def position(self):
        return f"{self.line_num}:{self.pos}"
    
    # Format the return value (e.g. 11:1:'end-of-text' or 9:15:'ID' a)
    def __str__(self):
        return f"{self.line_num}:{self.pos}:'{self.kind}' {self.value if (self.kind == 'ID' or self.kind == 'NUM') else ''}"