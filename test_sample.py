"""
Test a sample SPL program through all three compiler phases:
1. Lexer (tokenization)
2. Parser (syntax analysis) 
3. Type Checker (semantic analysis)
"""

from lexer import SPLLexer
from parser import parse_spl
from typechecker import type_check_spl

def test_sample_program():
    """Test a sample SPL program through all three phases."""
    
    # Sample SPL program
    sample_code = """
    glob { total }
    proc { }
    func {
        add ( x y ) {
            local { result }
            result = ( x plus y );
            return result
        }
    }
    main {
        var { a b }
        a = 10;
        b = 20;
        total = add ( a b );
        print total;
        halt
    }
    """
    
    print("=" * 80)
    print("SPL COMPILER - THREE PHASE TEST")
    print("=" * 80)
    print("\nSample Program:")
    print(sample_code)
    print("=" * 80)
    
    # Phase 1: Lexer (Tokenization)
    print("\nPHASE 1: LEXER (Tokenization)")
    print("-" * 40)
    lexer = SPLLexer()
    tokens = list(lexer.tokenize(sample_code))
    print(f"✓ Generated {len(tokens)} tokens")
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
        print("✓ Parsing successful!")
        print("Parse tree structure:")
        print(f"  Root: {parse_tree[0]}")
        print(f"  Global variables: {len(parse_tree[1])} variables")
        print(f"  Procedures: {len(parse_tree[2])} procedures")
        print(f"  Functions: {len(parse_tree[3])} functions")
        print(f"  Main program: {len(parse_tree[4][1])} local variables, {len(parse_tree[4][2])} instructions")
    else:
        print("✗ Parsing failed!")
        return False
    
    # Phase 3: Type Checker (Semantic Analysis)
    print("\nPHASE 3: TYPE CHECKER (Semantic Analysis)")
    print("-" * 40)
    type_check_result = type_check_spl(parse_tree)
    if type_check_result:
        print("✓ Type checking passed!")
    else:
        print("✗ Type checking failed!")
        return False
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print("✓ Phase 1 (Lexer): Tokenization successful")
    print("✓ Phase 2 (Parser): Syntax analysis successful") 
    print("✓ Phase 3 (Type Checker): Semantic analysis successful")
    print("\n🎉 ALL THREE PHASES COMPLETED SUCCESSFULLY!")
    print("Your SPL program is syntactically and semantically correct.")
    print("=" * 80)
    
    return True

if __name__ == "__main__":
    test_sample_program()