"""
Test a sample SPL program with semantic errors through all three compiler phases:
1. Lexer (tokenization)
2. Parser (syntax analysis) 
3. Scope Analyzer (semantic analysis)
"""

from lexer import SPLLexer
from parser import parse_spl
from semantic_analyzer import analyze_spl_semantics, print_semantic_errors, ScopeAnalyzer

def test_sample_program_with_errors():
    """Test a sample SPL program with semantic errors through all three phases."""
    
    # Sample SPL program with semantic errors
    sample_code = """
    glob { x x }  // Duplicate global variable
    proc { }
    func {
        add ( x y ) {
            local { result }
            result = ( x plus y );
            return result
        }
    }
    main {
        var { a }
        b = 10;  // Undeclared variable 'b'
        total = add ( a 5 );  // Undeclared variable 'total'
        print b;
        halt
    }
    """
    
    print("=" * 80)
    print("SPL COMPILER - THREE PHASE TEST (WITH ERRORS)")
    print("=" * 80)
    print("\nSample Program (with intentional errors):")
    print(sample_code)
    print("=" * 80)
    
    # Phase 1: Lexer (Tokenization)
    print("\nPHASE 1: LEXER (Tokenization)")
    print("-" * 40)
    lexer = SPLLexer()
    tokens = list(lexer.tokenize(sample_code))
    print(f"OK: Generated {len(tokens)} tokens")
    print("First 10 tokens:")
    for i, token in enumerate(tokens[:10]):
        print(f"  {i+1:2d}. {token.type:12s} = '{token.value}'")
    if len(tokens) > 10:
        print(f"  ... and {len(tokens) - 10} more tokens")
    
    # Phase 2: Parser (Syntax Analysis)
    print("\nPHASE 2: PARSER (Syntax Analysis)")
    print("-" * 40)
    parse_tree = parse_spl(sample_code)
    if parse_tree:
        print("OK: Parsing successful!")
        print("Parse tree structure:")
        print(f"  Root: {parse_tree[0]}")
        print(f"  Global variables: {len(parse_tree[2])} variables")
        print(f"  Procedures: {len(parse_tree[3])} procedures")
        print(f"  Functions: {len(parse_tree[4])} functions")
        print(f"  Main program: {len(parse_tree[5][2])} local variables, {len(parse_tree[5][3])} instructions")
    else:
        print("FAIL: Parsing failed!")
        return False
    
    # Phase 3: Scope Analyzer (Semantic Analysis)
    print("\nPHASE 3: SCOPE ANALYZER (Semantic Analysis)")
    print("-" * 40)
    
    # Create scope analyzer and analyze
    analyzer = ScopeAnalyzer()
    success, errors = analyzer.analyze(parse_tree)
    
    if success:
        print("OK: Scope analysis passed!")
        print_semantic_errors(errors)
    else:
        print("FAIL: Scope analysis failed!")
        print_semantic_errors(errors)
    
    # Display Symbol Table
    print("\nSYMBOL TABLE:")
    print("-" * 40)
    print("Scopes and Symbols:")
    for scope_id, scope in analyzer.symbol_table.scopes.items():
        print(f"\nScope: {scope_id} ({scope.scope_type.value})")
        if scope.parent_scope_id:
            print(f"  Parent: {scope.parent_scope_id}")
        if scope.symbols:
            print("  Symbols:")
            for name, symbol in scope.symbols.items():
                print(f"    {name}: {symbol.symbol_type.value} (node_id: {symbol.node_id})")
        else:
            print("  (No symbols)")
    
    # Display Symbol Table Entries by Node ID
    print(f"\nSymbol Table Entries (by Node ID):")
    print("-" * 40)
    for node_id, entry in analyzer.symbol_table.entries.items():
        print(f"Node {node_id}: {entry.name} ({entry.symbol_type.value}) in {entry.scope_id}")
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print("OK: Phase 1 (Lexer): Tokenization successful")
    print("OK: Phase 2 (Parser): Syntax analysis successful") 
    if success:
        print("OK: Phase 3 (Scope Analyzer): Semantic analysis successful")
        print("\nSUCCESS: ALL THREE PHASES COMPLETED SUCCESSFULLY!")
        print("Your SPL program is syntactically and semantically correct.")
    else:
        print("FAIL: Phase 3 (Scope Analyzer): Semantic analysis found errors")
        print(f"\nFAILURE: FOUND {len(errors)} SEMANTIC ERROR(S)!")
        print("Your SPL program has semantic issues that need to be fixed.")
    print("=" * 80)
    
    return success

if __name__ == "__main__":
    test_sample_program_with_errors()
