class LexicalAnalyzer:
    def __init__(self, filepath):
        # GIVEN
        self.filepath: str = filepath
        # RESERVED VALUES
        self.reserved: dict = {
            "keywords": ["program", "true", "false", "if", "then", "else", "while", "do", "end", "print", "int", "bool"],
            "symbols": [":=", ";", ":", "<", ">", "*", "<=", ">=", "!=", "+", "-", "or", "/", "mod", "and", "not," "(", ")"]
        }
        # LOOKAHEAD
        self.lookahead: str = "" # Value of lookahead char
        self.pos: int = -1 # Position of lookahead
        self.line_num: int = 1 # Line number of the lookahead
        self.pos_offset: int = 0
        self.comment_flag: bool = False # Should we ignore the remainder of the line?
        # LEXEMES
        self.lexemes = []
    
    def next(self):
        with open(self.filepath, 'r') as f:
            # Read one char. If it is not a space, add it to the current lexeme
            # if the lexeme is new, set its start position to the current position
            # keep going until the char is a whitespace (lexeme finished) or char is 
            # not approved (invalid)
            
            # If the char is a reserved keyword/symbol, we need to handle that as it occurs
            
            self.pos += 1 # increment to move past current lexeme
            start_pos = -1 # reset start position for current lexeme
            lexeme = "" # reset lexeme
            
            while self.validate(self.lookahead):
                if(start_pos == -1):
                    start_pos = self.pos
                    
                # Move cursor right once
                f.seek(self.pos)
                self.lookahead = f.read(1)
                

                if(lexeme == "//"):
                    self.comment_flag = True
                
                # Ignore whitespace
                if(self.lookahead.isspace() and lexeme.strip() == ""):
                    start_pos = -1
                    self.pos += 1
                    continue
                # When the lexeme is finished
                elif (self.lookahead.isspace()): 
                    if not self.comment_flag:
                        if (len(self.lexemes) == 0): start_pos += 1 # The first lexeme should start at char 1 
                        self.lexemes.append(Lexeme(lexeme, (start_pos - self.pos_offset), self.line_num, reserved=self.reserved))
                        print(self.lexemes[-1])
                     
                    # Track if there was a new line
                    if self.lookahead == "\n":
                        self.line_num += 1
                        self.pos_offset = self.pos
                        self.comment_flag = False
                    
                    break
                
                # Add current lookahead to the lexeme being built
                lexeme += self.lookahead
                self.pos += 1         

    def kind(self):
        return self.lexemes[-1].kind if self.lexemes else ""

    def value(self):
        return self.lexemes[-1].value if self.lexemes else ""

    def position(self):
        return self.lexemes[-1].pos if self.lexemes else ""
    
    def validate(self, str):
        return True
        
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
        if(self.value.isdigit()):
            self.kind = "NUM"
        # Keyword
        elif self.value in self.__reserved["keywords"]:
            self.kind = self.value
        # Symbol
        elif self.value in self.__reserved["symbols"]:
            self.kind = self.value
        # End of file
        elif self.value == ".":
            self.kind == "end-of-text"
        else:
            self.kind = "ID"
    
    def __str__(self):
        return f"{self.line_num}:{self.pos}:'{self.kind}' {self.value if (self.kind == "ID" or self.kind == "NUM") else ""}"
            


def main():
    filepath = parse_input_file()
    a = LexicalAnalyzer(filepath=filepath)

    a.next()
    # print(a.position(), a.kind(), a.value())
    while(a.kind() != 'end-of-text'):
        a.next()
        # print(a.position(), a.kind(), a.value())

def parse_input_file():
    filepath = input("Enter the language file path: ")
    try:
        with open(filepath, 'r') as f:
            # print(f, " file exists!")
            return filepath
    except:
        print("That filepath does not exist!")
    



main()