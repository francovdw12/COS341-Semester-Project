from sly import Lexer

class SPLLexer(Lexer):
    # List of token names
    tokens = {
        # Keywords
        GLOB, PROC, FUNC, MAIN, VAR, LOCAL, HALT, PRINT, WHILE, DO, UNTIL, 
        IF, ELSE, RETURN,
        # Operators
        EQ, GT, OR, AND, PLUS, MINUS, MULT, DIV, NEG, NOT,
        # Punctuation
        LPAREN, RPAREN, LBRACE, RBRACE, SEMICOLON, ASSIGN,
        # Identifiers and literals
        NAME, NUMBER, STRING
    }

    # String containing ignored characters (spaces, tabs, newlines)
    ignore = ' \t\n'

    # Literals - single character tokens
    LPAREN = r'\('
    RPAREN = r'\)'
    LBRACE = r'\{'
    RBRACE = r'\}'
    SEMICOLON = r';'
    ASSIGN = r'='
    GT = r'>'

    # Ignore comments (// to end of line)
    @_(r'//.*')
    def COMMENT(self, t):
        pass

    # User-defined name: [a-z][a-z]*[0-9]* (starts with lowercase, followed by lowercase, then optional digits)
    # This must come BEFORE keywords to check if it's a keyword
    @_(r'[a-z][a-z]*[0-9]*')
    def NAME(self, t):
        # Check if the matched name is actually a keyword
        keywords = {
            'return': 'RETURN', 'local': 'LOCAL', 'glob': 'GLOB', 'proc': 'PROC',
            'func': 'FUNC', 'main': 'MAIN', 'var': 'VAR', 'halt': 'HALT',
            'print': 'PRINT', 'while': 'WHILE', 'do': 'DO', 'until': 'UNTIL',
            'if': 'IF', 'else': 'ELSE', 'eq': 'EQ', 'gt': 'GT', 'or': 'OR', 'and': 'AND',
            'plus': 'PLUS', 'minus': 'MINUS', 'mult': 'MULT', 'div': 'DIV',
            'neg': 'NEG', 'not': 'NOT'
        }
        t.type = keywords.get(t.value, 'NAME')
        return t

    # String literal: max 15 characters between quotes (letters, digits, and spaces)
    @_(r'\"[a-zA-Z0-9 ]{0,15}\"')
    def STRING(self, t):
        t.value = t.value[1:-1]  # Remove quotes
        return t

    # Number: 0 or [1-9][0-9]* (either exactly 0, or starts with 1-9)
    @_(r'0|[1-9][0-9]*')
    def NUMBER(self, t):
        t.value = int(t.value)
        return t

    # Error handling
    def error(self, t):
        print(f'Illegal character {t.value[0]!r} at line {self.lineno}')
        self.index += 1
