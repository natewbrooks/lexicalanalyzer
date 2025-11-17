from lexicalanalyzer import LexicalAnalyzer, Lexeme

class SyntaxParser:
    def __init__(self, la: LexicalAnalyzer):
        self.la = la
        self.curr: Lexeme = None
        self.next()
        self.program()
        
    # Helpers
    def next(self):
        self.la.next()
        self.curr = self.la.last()
        print(self.curr)
        
    def match(self, sym: str):
        if self.curr and self.curr.kind == sym:
            self.next()
        else:
            raise self.expected(sym)
    
    def expected(self, *args):
        if self.curr.kind not in args:
            raise SyntaxError(f"Bad symbol '{self.curr.kind}' at {self.curr.position()}, " f"expected ({', '.join([f'\'{a}\'' for a in args])}) instead.")

    # Grammar Rules
    def program(self):
        self.match('program')
        self.match('ID')
        self.match(':')
        self.body()            
        self.match('.')
        
    def body(self):
        if self.curr.kind in ('bool', 'int'):
            self.declarations()
        self.statements()
    
    def declarations(self):
        self.declaration()
        while self.curr.kind in ('bool', 'int'):
            self.declaration()
    
    def declaration(self):
        assert self.curr.kind in ('bool', 'int')
        self.next()
        id_line = self.curr.line_num
        self.match('ID')

        if self.curr.kind not in (',', ';'):
            if self.curr.line_num != id_line:
                self.expected(';')
            else:
                self.expected(',', ';')

        while self.curr.kind == ',':
            self.next()
            id_line = self.curr.line_num
            self.match('ID')
            if self.curr.kind not in (',', ';'):
                if self.curr.line_num != id_line:
                    self.expected(';')
                else:
                    self.expected(',', ';')

        self.match(';')


    def statements(self):
        self.statement()
        while self.curr.kind == ";":
            self.next()
            self.statement()
    
    def statement(self):
        if self.curr.kind == 'ID':
            self.assignment_statement()
        elif self.curr.kind == 'if':
            self.conditional_statement()
        elif self.curr.kind == 'while':
            self.iterative_statement()
        elif self.curr.kind == 'print':
            self.print_statement()
        else:
            self.expected('ID', 'if', 'while', 'print')
    
    def assignment_statement(self):
        assert self.curr.kind == 'ID'
        self.match('ID')
        self.match(':=')
        self.expression()
    
    def conditional_statement(self):
        assert self.curr.kind == 'if'
        self.match('if')
        self.expression()
        self.match('then')
        self.body()
        # Optional else clause
        if self.curr.kind == 'else':
            self.match('else')
            self.body()
        self.match('end')
    
    def iterative_statement(self):
        assert self.curr.kind == 'while'
        self.match('while')
        self.expression()
        self.match('do')
        self.body()
        self.match('end')
    
    def print_statement(self):
        assert self.curr.kind == 'print'
        self.match('print')
        self.expression()
    
    def expression(self):
        self.simple_expression()
        if self.curr.kind in ('<', '=<', '=', '!=', '>=', '>'):
            self.relational_operator()
            self.simple_expression()
    
    def relational_operator(self):
        self.match(self.curr.kind)  # one of '<', '=<', '=', '!=', '>=', '>'    
    
    def simple_expression(self):
        self.term()
        while self.curr.kind in ('+', '-', 'or'):
            self.additive_operator()
            self.term()
            
    def term(self):
        self.factor()
        while self.curr.kind in ('*', '/', 'mod', 'and'):
            self.multiplicative_operator()
            self.factor()
        if self.curr.kind in ('end-of-text',):
            self.expected('*', '/', 'mod', 'and', '+', '-', 'or', '<', '=<', '=', '!=', '>=', '>', ';', '.')
    
    def additive_operator(self):
        self.match(self.curr.kind)  # one of '+', '-', 'or'
    
    def multiplicative_operator(self):
        self.match(self.curr.kind)  # one of '*', '/', 'mod', 'and'
         
    def factor(self):
        if self.curr.kind in ('-', 'not'):
            self.unary_operator()
            self.factor()
        elif self.curr.kind == 'ID':
            self.match('ID')
        elif self.curr.kind == 'NUM':
            self.integer_literal()
        elif self.curr.kind in ('true', 'false'):
            self.boolean_literal()
        elif self.curr.kind == '(':
            self.match('(')
            self.expression()
            if self.curr.kind != ')':
                self.expected('*', '/', 'and', '+', '-', 'or', ')')
            self.match(')')
        else:
            self.expected('NUM', 'false', 'true', 'ID', '(', '-', 'not')

    # def literal(self):
    #     pass
    
    def unary_operator(self):
        self.match(self.curr.kind)  # one of '-', 'not'
    
    def integer_literal(self):
        self.match('NUM')
    
    def boolean_literal(self):
        if self.curr.kind in ('true', 'false'):
            self.next()
        else:
            self.expected('true', 'false')