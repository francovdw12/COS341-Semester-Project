"""
SPL Parser Implementation (with line numbers on leaves)
"""

from sly import Parser
from lexer import SPLLexer

__all__ = ['SPLParser', 'parse_spl', 'print_parse_tree']

class SPLParser(Parser):
    tokens = SPLLexer.tokens

    precedence = (
        ('left', 'OR'),
        ('left', 'AND'),
        ('left', 'EQ', 'GT'),
        ('left', 'PLUS', 'MINUS'),
        ('left', 'MULT', 'DIV'),
        ('right', 'NEG', 'NOT'),
    )

    @staticmethod
    def _unpack(v):
        # NAME/NUMBER/STRING tokens carry (value, lineno)
        if isinstance(v, tuple) and len(v) == 2 and isinstance(v[1], int):
            return v[0], v[1]
        return v, None

    # SPL_PROG
    @_('GLOB LBRACE variables RBRACE PROC LBRACE procdefs RBRACE '
       'FUNC LBRACE funcdefs RBRACE MAIN LBRACE mainprog RBRACE')
    def spl_prog(self, p):
        return ('SPL_PROG', p.variables, p.procdefs, p.funcdefs, p.mainprog)

    # VARIABLES
    @_('empty')
    def variables(self, p): return []

    @_('var variables')
    def variables(self, p): return [p.var] + p.variables

    # VAR & NAME (carry line numbers)
    @_('NAME')
    def var(self, p):
        s, line = self._unpack(p.NAME)
        return ('VAR', s, line)

    @_('NAME')
    def name(self, p):
        s, line = self._unpack(p.NAME)
        return ('NAME', s, line)

    # PROCDEFS
    @_('empty')
    def procdefs(self, p): return []

    @_('pdef procdefs')
    def procdefs(self, p): return [p.pdef] + p.procdefs

    # PDEF
    @_('name LPAREN param RPAREN LBRACE body RBRACE')
    def pdef(self, p):
        return ('PDEF', p.name, p.param, p.body)

    # FUNCDEFS
    @_('empty')
    def funcdefs(self, p): return []

    @_('fdef funcdefs')
    def funcdefs(self, p): return [p.fdef] + p.funcdefs

    # FDEF
    @_('name LPAREN param RPAREN LBRACE LOCAL LBRACE maxthree RBRACE instrs SEMICOLON RETURN atom RBRACE')
    def fdef(self, p):
        return ('FDEF', p.name, p.param, ('BODY', p.maxthree, p.instrs), p.atom)

    @_('name LPAREN param RPAREN LBRACE LOCAL LBRACE maxthree RBRACE RETURN atom RBRACE')
    def fdef(self, p):
        return ('FDEF', p.name, p.param, ('BODY', p.maxthree, []), p.atom)

    # BODY
    @_('LOCAL LBRACE maxthree RBRACE algo')
    def body(self, p):
        return ('BODY', p.maxthree, p.algo)

    @_('instr')
    def instrs(self, p): return [p.instr]

    @_('instrs SEMICOLON instr')
    def instrs(self, p): return p.instrs + [p.instr]

    # PARAM
    @_('maxthree')
    def param(self, p): return ('PARAM', p.maxthree)

    # MAXTHREE
    @_('empty')
    def maxthree(self, p): return []

    @_('var')
    def maxthree(self, p): return [p.var]

    @_('var var')
    def maxthree(self, p): return [p.var0, p.var1]

    @_('var var var')
    def maxthree(self, p): return [p.var0, p.var1, p.var2]

    # MAINPROG
    @_('VAR LBRACE variables RBRACE algo')
    def mainprog(self, p):
        return ('MAINPROG', p.variables, p.algo)

    # ATOM
    @_('var')
    def atom(self, p):
        return ('ATOM_VAR', p.var)  # ('VAR', name, line)

    @_('NUMBER')
    def atom(self, p):
        val, line = self._unpack(p.NUMBER)
        return ('ATOM_NUM', val, line)

    # ALGO
    @_('instr')
    def algo(self, p): return [p.instr]

    @_('instr SEMICOLON algo')
    def algo(self, p): return [p.instr] + p.algo

    # INSTR
    @_('HALT')
    def instr(self, p): return ('INSTR_HALT',)

    @_('PRINT output')
    def instr(self, p): return ('INSTR_PRINT', p.output)

    @_('name LPAREN input RPAREN')
    def instr(self, p): return ('INSTR_CALL', p.name, p.input)

    @_('assign')
    def instr(self, p): return p.assign

    @_('loop')
    def instr(self, p): return p.loop

    @_('branch')
    def instr(self, p): return p.branch

    # ASSIGN
    @_('var ASSIGN name LPAREN input RPAREN')
    def assign(self, p):
        return ('ASSIGN_CALL', p.var, p.name, p.input)

    @_('var ASSIGN term')
    def assign(self, p):
        return ('ASSIGN_TERM', p.var, p.term)

    # LOOP
    @_('WHILE term LBRACE algo RBRACE')
    def loop(self, p): return ('LOOP_WHILE', p.term, p.algo)

    @_('DO LBRACE algo RBRACE UNTIL term')
    def loop(self, p): return ('LOOP_DO_UNTIL', p.algo, p.term)

    # BRANCH
    @_('IF term LBRACE algo RBRACE')
    def branch(self, p): return ('BRANCH_IF', p.term, p.algo)

    @_('IF term LBRACE algo RBRACE ELSE LBRACE algo RBRACE')
    def branch(self, p): return ('BRANCH_IF_ELSE', p.term, p.algo0, p.algo1)

    # OUTPUT
    @_('atom')
    def output(self, p): return ('OUTPUT_ATOM', p.atom)

    @_('STRING')
    def output(self, p):
        s, line = self._unpack(p.STRING)
        return ('OUTPUT_STRING', s, line)

    # INPUT
    @_('empty')
    def input(self, p): return []

    @_('atom')
    def input(self, p): return [p.atom]

    @_('atom atom')
    def input(self, p): return [p.atom0, p.atom1]

    @_('atom atom atom')
    def input(self, p): return [p.atom0, p.atom1, p.atom2]

    # TERM
    @_('atom')
    def term(self, p): return ('TERM_ATOM', p.atom)

    @_('LPAREN unop term RPAREN')
    def term(self, p): return ('TERM_UNOP', p.unop, p.term)

    @_('LPAREN term binop term RPAREN')
    def term(self, p): return ('TERM_BINOP', p.term0, p.binop, p.term1)

    # UNOP / BINOP
    @_('NEG')
    def unop(self, p): return 'NEG'

    @_('NOT')
    def unop(self, p): return 'NOT'

    @_('EQ')
    def binop(self, p): return 'EQ'

    @_('GT')
    def binop(self, p): return 'GT'

    @_('OR')
    def binop(self, p): return 'OR'

    @_('AND')
    def binop(self, p): return 'AND'

    @_('PLUS')
    def binop(self, p): return 'PLUS'

    @_('MINUS')
    def binop(self, p): return 'MINUS'

    @_('MULT')
    def binop(self, p): return 'MULT'

    @_('DIV')
    def binop(self, p): return 'DIV'

    # Empty
    @_('')
    def empty(self, p): pass

    # Error handling
    def error(self, p):
        if p:
            print(f"Syntax error at token {p.type} ('{p.value}') at line {p.lineno}")
        else:
            print("Syntax error at EOF")

# -------- public helpers (TOP-LEVEL, not in __main__) --------

def parse_spl(code: str):
    """Parse SPL source code and return AST (or None on failure)."""
    lexer = SPLLexer()
    parser = SPLParser()
    try:
        return parser.parse(lexer.tokenize(code))
    except Exception as e:
        print(f"Parsing failed: {e}")
        return None

def print_parse_tree(tree, indent=0):
    if tree is None:
        print("  " * indent + "None"); return
    if isinstance(tree, tuple):
        print("  " * indent + f"({tree[0]}")
        for item in tree[1:]:
            print_parse_tree(item, indent + 1)
        print("  " * indent + ")")
    elif isinstance(tree, list):
        print("  " * indent + "[")
        for item in tree:
            print_parse_tree(item, indent + 1)
        print("  " * indent + "]")
    else:
        print("  " * indent + str(tree))
