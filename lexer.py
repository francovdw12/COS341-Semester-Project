from sly import Lexer

class SPLLexer(Lexer):
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

    # Important: don't ignore '\n' here; track it in a rule to keep lineno accurate
    ignore = ' \t'

    @_(r'\n+')
    def ignore_newline(self, t):
        self.lineno += t.value.count('\n')

    # Punctuation / symbols
    LPAREN = r'\('
    RPAREN = r'\)'
    LBRACE = r'\{'
    RBRACE = r'\}'
    SEMICOLON = r';'
    ASSIGN = r'='
    GT = r'>'

    # Comments
    @_(r'//.*')
    def COMMENT(self, t):
        pass

    # Names & keywords
    @_(r'[a-z][a-z]*[0-9]*')
    def NAME(self, t):
        keywords = {
            'return': 'RETURN', 'local': 'LOCAL', 'glob': 'GLOB', 'proc': 'PROC',
            'func': 'FUNC', 'main': 'MAIN', 'var': 'VAR', 'halt': 'HALT',
            'print': 'PRINT', 'while': 'WHILE', 'do': 'DO', 'until': 'UNTIL',
            'if': 'IF', 'else': 'ELSE', 'eq': 'EQ', 'or': 'OR', 'and': 'AND',
            'plus': 'PLUS', 'minus': 'MINUS', 'mult': 'MULT', 'div': 'DIV',
            'neg': 'NEG', 'not': 'NOT'
        }
        t.type = keywords.get(t.value, 'NAME')
        # carry line numbers on identifier leaves
        if t.type == 'NAME':
            t.value = (t.value, t.lineno)  # ('foo', 12)
        return t

    # String literal: 0–15 alnum chars
    @_(r'\"[a-zA-Z0-9]{0,15}\"')
    def STRING(self, t):
        t.value = (t.value[1:-1], t.lineno)  # ('text', line)
        return t

    # Integer
    @_(r'0|[1-9][0-9]*')
    def NUMBER(self, t):
        t.value = (int(t.value), t.lineno)   # (42, line)
        return t

    def error(self, t):
        print(f'Illegal character {t.value[0]!r} at line {self.lineno}')
        self.index += 1
