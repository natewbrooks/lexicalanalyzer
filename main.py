class LexicalAnalyzer:
    def __init__(self, filepath):
        self.filepath: str = filepath
        # RESERVED
        self._keywords = ["program", "true", "false", "if", "int", "str"]
        self._symbols = [":=", ";", ":"]
        # LOOKAHEAD
        self._lookahead: str = "" # Value of lookahead char
        self._pos: int = -1 # Position of lookahead
        # LEXEME
        self._lexeme: str = "" # Value of the current lexeme string
        self._start_pos: int = -1 # Start position of current lexeme
        self._kind: str = "" # Type of current lookahead
        self._line_num: int = 0 # Line number of the current lexeme
    
    def next(self):
        with open(self.filepath, 'r') as f:
            # Read one char. If it is not a space, add it to the current lexeme
            # if the lexeme is new, set its start position to the current position
            # keep going until the char is a whitespace (lexeme finished) or char is 
            # not approved (invalid)
            self._pos += 1 # increment to move past current lexeme
            self._start_pos = -1 # reset start position for current lexeme
            self._lexeme = "" # reset lexeme
            self._kind = ""
            
            while self.validate(self._lookahead):
                if(self._start_pos == -1):
                    self._start_pos = self._pos
                    
                # Move cursor right once
                f.seek(self._pos)
                self._lookahead = f.read(1)
                
                # Track new line
                if(self._lookahead == "\n"):
                    self._line_num += 1
                elif(self._lookahead == "."):
                    self._kind = "end-of-text"
                    break
                
                # If it is a space, lexeme is finished
                if(self._lookahead.isspace()):
                    print(f"{self._start_pos}:{self._line_num}:'{self.kind()}' " + self._lexeme)
                    break
                
                # Increment lookahead by 1
                self._lexeme += self._lookahead
                self._pos += 1         
                
            
        return self._lookahead

    def kind(self):
        # Number
        if self._kind == "":
            if(self._lexeme.isdigit()):
                self._kind = "NUM"
            # Keyword
            elif self._lexeme in self._keywords:
                self._kind = self._lexeme
            # Symbol
            elif self._lexeme in self._symbols:
                self._kind = self._lexeme
            else:
                self._kind = "ID"
        else:
            self._kind = "end-of-text"
            

        return self._kind

    def value(self):
        pass

    def position(self):
        return self.position
    
    def validate(self, str):
        return True
        
    def __str__(self):
        return "file: " + self.filepath
        


def main():
    filepath = parse_input_file()
    a = LexicalAnalyzer(filepath=filepath)
    # print(a)
    # a.next()
    # a.kind()
    # a.next()
    # a.kind()
    
    
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