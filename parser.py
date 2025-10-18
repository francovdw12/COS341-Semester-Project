"""
SPL Parser Implementation
COS341 Semester Project 2025

This parser implements the SPL grammar specification using SLY.
The grammar is not in LL(1) format, so we use SLY's LR parser.
"""

from sly import Parser
from lexer import SPLLexer


class SPLParser(Parser):
    # Get the token list from the lexer
    tokens = SPLLexer.tokens
    
    # Grammar rules with precedence to resolve ambiguities
    # Lower precedence first
    precedence = (
        ('left', 'OR'),
        ('left', 'AND'),
        ('left', 'EQ', 'GT'),
        ('left', 'PLUS', 'MINUS'),
        ('left', 'MULT', 'DIV'),
        ('right', 'NEG', 'NOT'),
    )
    
    # ========================================================================
    # SPL_PROG - The root of the program
    # SPL_PROG ::= glob { VARIABLES } proc { PROCDEFS } func { FUNCDEFS } main { MAINPROG }
    # ========================================================================
    
    @_('GLOB LBRACE variables RBRACE PROC LBRACE procdefs RBRACE FUNC LBRACE funcdefs RBRACE MAIN LBRACE mainprog RBRACE')
    def spl_prog(self, p):
        return ('SPL_PROG', p.variables, p.procdefs, p.funcdefs, p.mainprog)
    
    # ========================================================================
    # VARIABLES - Global or local variable declarations
    # VARIABLES ::= (empty)
    # VARIABLES ::= VAR VARIABLES
    # ========================================================================
    
    @_('empty')
    def variables(self, p):
        return []
    
    @_('var variables')
    def variables(self, p):
        return [p.var] + p.variables
    
    # ========================================================================
    # VAR and NAME - User-defined identifiers
    # VAR ::= user-defined-name
    # NAME ::= user-defined-name
    # ========================================================================
    
    @_('NAME')
    def var(self, p):
        return ('VAR', p.NAME)
    
    @_('NAME')
    def name(self, p):
        return ('NAME', p.NAME)
    
    # ========================================================================
    # PROCDEFS - Procedure definitions
    # PROCDEFS ::= (empty)
    # PROCDEFS ::= PDEF PROCDEFS
    # ========================================================================
    
    @_('empty')
    def procdefs(self, p):
        return []
    
    @_('pdef procdefs')
    def procdefs(self, p):
        return [p.pdef] + p.procdefs
    
    # ========================================================================
    # PDEF - Single procedure definition
    # PDEF ::= NAME ( PARAM ) { BODY }
    # ========================================================================
    
    @_('name LPAREN param RPAREN LBRACE body RBRACE')
    def pdef(self, p):
        return ('PDEF', p.name, p.param, p.body)
    
    # ========================================================================
    # FUNCDEFS - Function definitions
    # FUNCDEFS ::= (empty)
    # FUNCDEFS ::= FDEF FUNCDEFS
    # ========================================================================
    
    @_('empty')
    def funcdefs(self, p):
        return []
    
    @_('fdef funcdefs')
    def funcdefs(self, p):
        return [p.fdef] + p.funcdefs
    
    # ========================================================================
    # FDEF - Single function definition  
    # FDEF ::= NAME ( PARAM ) { BODY ; return ATOM }
    # The BODY contains local variables and algorithm (which may be empty conceptually)
    # ========================================================================
    
    # Function with instructions before return
    @_('name LPAREN param RPAREN LBRACE LOCAL LBRACE maxthree RBRACE instrs SEMICOLON RETURN atom RBRACE')
    def fdef(self, p):
        return ('FDEF', p.name, p.param, ('BODY', p.maxthree, p.instrs), p.atom)
    
    # Function with no instructions before return (just local vars)
    @_('name LPAREN param RPAREN LBRACE LOCAL LBRACE maxthree RBRACE RETURN atom RBRACE')
    def fdef(self, p):
        return ('FDEF', p.name, p.param, ('BODY', p.maxthree, []), p.atom)
    
    # ========================================================================
    # BODY - Procedure body
    # BODY ::= local { MAXTHREE } ALGO
    # ========================================================================
    
    @_('LOCAL LBRACE maxthree RBRACE algo')
    def body(self, p):
        return ('BODY', p.maxthree, p.algo)
    
    # Helper for building instruction sequences without consuming final semicolon
    @_('instr')
    def instrs(self, p):
        return [p.instr]
    
    @_('instrs SEMICOLON instr')
    def instrs(self, p):
        return p.instrs + [p.instr]
    
    # ========================================================================
    # PARAM - Parameters (same as MAXTHREE)
    # PARAM ::= MAXTHREE
    # ========================================================================
    
    @_('maxthree')
    def param(self, p):
        return ('PARAM', p.maxthree)
    
    # ========================================================================
    # MAXTHREE - Up to three variables
    # MAXTHREE ::= (empty)
    # MAXTHREE ::= VAR
    # MAXTHREE ::= VAR VAR
    # MAXTHREE ::= VAR VAR VAR
    # ========================================================================
    
    @_('empty')
    def maxthree(self, p):
        return []
    
    @_('var')
    def maxthree(self, p):
        return [p.var]
    
    @_('var var')
    def maxthree(self, p):
        return [p.var0, p.var1]
    
    @_('var var var')
    def maxthree(self, p):
        return [p.var0, p.var1, p.var2]
    
    # ========================================================================
    # MAINPROG - Main program
    # MAINPROG ::= var { VARIABLES } ALGO
    # ========================================================================
    
    @_('VAR LBRACE variables RBRACE algo')
    def mainprog(self, p):
        return ('MAINPROG', p.variables, p.algo)
    
    # ========================================================================
    # ATOM - Basic values (variables or numbers)
    # ATOM ::= VAR
    # ATOM ::= number
    # ========================================================================
    
    @_('var')
    def atom(self, p):
        return ('ATOM_VAR', p.var)
    
    @_('NUMBER')
    def atom(self, p):
        return ('ATOM_NUM', p.NUMBER)
    
    # ========================================================================
    # ALGO - Algorithm (sequence of instructions)
    # ALGO ::= INSTR
    # ALGO ::= INSTR ; ALGO
    # ========================================================================
    
    @_('instr')
    def algo(self, p):
        return [p.instr]
    
    @_('instr SEMICOLON algo')
    def algo(self, p):
        return [p.instr] + p.algo
    
    # ========================================================================
    # INSTR - Single instruction
    # INSTR ::= halt
    # INSTR ::= print OUTPUT
    # INSTR ::= NAME ( INPUT )
    # INSTR ::= ASSIGN
    # INSTR ::= LOOP
    # INSTR ::= BRANCH
    # ========================================================================
    
    @_('HALT')
    def instr(self, p):
        return ('INSTR_HALT',)
    
    @_('PRINT output')
    def instr(self, p):
        return ('INSTR_PRINT', p.output)
    
    @_('name LPAREN input RPAREN')
    def instr(self, p):
        return ('INSTR_CALL', p.name, p.input)
    
    @_('assign')
    def instr(self, p):
        return p.assign
    
    @_('loop')
    def instr(self, p):
        return p.loop
    
    @_('branch')
    def instr(self, p):
        return p.branch
    
    # ========================================================================
    # ASSIGN - Assignment statements
    # ASSIGN ::= VAR = NAME ( INPUT )
    # ASSIGN ::= VAR = TERM
    # ========================================================================
    
    @_('var ASSIGN name LPAREN input RPAREN')
    def assign(self, p):
        return ('ASSIGN_CALL', p.var, p.name, p.input)
    
    @_('var ASSIGN term')
    def assign(self, p):
        return ('ASSIGN_TERM', p.var, p.term)
    
    # ========================================================================
    # LOOP - Loop constructs
    # LOOP ::= while TERM { ALGO }
    # LOOP ::= do { ALGO } until TERM
    # ========================================================================
    
    @_('WHILE term LBRACE algo RBRACE')
    def loop(self, p):
        return ('LOOP_WHILE', p.term, p.algo)
    
    @_('DO LBRACE algo RBRACE UNTIL term')
    def loop(self, p):
        return ('LOOP_DO_UNTIL', p.algo, p.term)
    
    # ========================================================================
    # BRANCH - Conditional statements
    # BRANCH ::= if TERM { ALGO }
    # BRANCH ::= if TERM { ALGO } else { ALGO }
    # ========================================================================
    
    @_('IF term LBRACE algo RBRACE')
    def branch(self, p):
        return ('BRANCH_IF', p.term, p.algo)
    
    @_('IF term LBRACE algo RBRACE ELSE LBRACE algo RBRACE')
    def branch(self, p):
        return ('BRANCH_IF_ELSE', p.term, p.algo0, p.algo1)
    
    # ========================================================================
    # OUTPUT - Print output
    # OUTPUT ::= ATOM
    # OUTPUT ::= string
    # ========================================================================
    
    @_('atom')
    def output(self, p):
        return ('OUTPUT_ATOM', p.atom)
    
    @_('STRING')
    def output(self, p):
        return ('OUTPUT_STRING', p.STRING)
    
    # ========================================================================
    # INPUT - Function/procedure arguments
    # INPUT ::= (empty)
    # INPUT ::= ATOM
    # INPUT ::= ATOM ATOM
    # INPUT ::= ATOM ATOM ATOM
    # ========================================================================
    
    @_('empty')
    def input(self, p):
        return []
    
    @_('atom')
    def input(self, p):
        return [p.atom]
    
    @_('atom atom')
    def input(self, p):
        return [p.atom0, p.atom1]
    
    @_('atom atom atom')
    def input(self, p):
        return [p.atom0, p.atom1, p.atom2]
    
    # ========================================================================
    # TERM - Expressions
    # TERM ::= ATOM
    # TERM ::= ( UNOP TERM )
    # TERM ::= ( TERM BINOP TERM )
    # ========================================================================
    
    @_('atom')
    def term(self, p):
        return ('TERM_ATOM', p.atom)
    
    @_('LPAREN unop term RPAREN')
    def term(self, p):
        return ('TERM_UNOP', p.unop, p.term)
    
    @_('LPAREN term binop term RPAREN')
    def term(self, p):
        return ('TERM_BINOP', p.term0, p.binop, p.term1)
    
    # ========================================================================
    # UNOP - Unary operators
    # UNOP ::= neg
    # UNOP ::= not
    # ========================================================================
    
    @_('NEG')
    def unop(self, p):
        return 'NEG'
    
    @_('NOT')
    def unop(self, p):
        return 'NOT'
    
    # ========================================================================
    # BINOP - Binary operators
    # BINOP ::= eq | > | or | and | plus | minus | mult | div
    # ========================================================================
    
    @_('EQ')
    def binop(self, p):
        return 'EQ'
    
    @_('GT')
    def binop(self, p):
        return 'GT'
    
    @_('OR')
    def binop(self, p):
        return 'OR'
    
    @_('AND')
    def binop(self, p):
        return 'AND'
    
    @_('PLUS')
    def binop(self, p):
        return 'PLUS'
    
    @_('MINUS')
    def binop(self, p):
        return 'MINUS'
    
    @_('MULT')
    def binop(self, p):
        return 'MULT'
    
    @_('DIV')
    def binop(self, p):
        return 'DIV'
    
    # ========================================================================
    # Empty production
    # ========================================================================
    
    @_('')
    def empty(self, p):
        pass
    
    # ========================================================================
    # Error handling
    # ========================================================================
    
    def error(self, p):
        if p:
            print(f"Syntax error at token {p.type} ('{p.value}') at line {p.lineno}")
        else:
            print("Syntax error at EOF")


# ============================================================================
# Helper function to parse SPL code
# ============================================================================

def parse_spl(code):
    """
    Parse SPL source code and return the parse tree.
    
    Args:
        code (str): SPL source code
        
    Returns:
        Parse tree (nested tuples) or None if parsing fails
    """
    lexer = SPLLexer()
    parser = SPLParser()
    
    try:
        result = parser.parse(lexer.tokenize(code))
        return result
    except Exception as e:
        print(f"Parsing failed: {e}")
        return None


# ============================================================================
# Helper function to pretty-print the parse tree
# ============================================================================

def print_parse_tree(tree, indent=0):
    """
    Pretty-print the parse tree.
    
    Args:
        tree: Parse tree (nested tuples)
        indent: Current indentation level
    """
    if tree is None:
        print("  " * indent + "None")
        return
    
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


if __name__ == "__main__":
    # Test the parser with a simple program
    test_program = """
    glob { x y }
    proc { }
    func { }
    main {
        var { counter }
        counter = 5;
        print counter;
        halt
    }
    """
    
    print("=" * 80)
    print("SPL Parser Test")
    print("=" * 80)
    print("\nInput Program:")
    print(test_program)
    print("\n" + "=" * 80)
    print("Parse Tree:")
    print("=" * 80)
    
    parse_tree = parse_spl(test_program)
    
    if parse_tree:
        print("\n✓ Parsing successful!\n")
        print_parse_tree(parse_tree)
    else:
        print("\n✗ Parsing failed!")
