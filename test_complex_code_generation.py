"""
Test program for complex intermediate code generation
Demonstrates all code generation features including control structures
"""

from lexer import SPLLexer
from parser import parse_spl
from semantic_analyzer import analyze_spl_semantics, print_semantic_errors, ScopeAnalyzer
from type_checker import check_spl_types, print_type_errors
from code_generator import generate_intermediate_code

def test_complex_code_generation():
    """Test program with complex constructs for comprehensive code generation"""
    
    # Complex program with various constructs
    sample_code = """
    glob { counter result }
    proc {
        increment ( ) {
            local { }
            counter = ( counter plus 1 )
        }
        
        reset ( ) {
            local { }
            counter = 0
        }
    }
    func {
        calculate ( x y ) {
            local { temp }
            temp = ( x plus y );
            return temp
        }
        
        maximum ( a b ) {
            local { result }
            if ( a > b ) {
                result = a
            } else {
                result = b
            };
            return result
        }
    }
    main {
        var { a b c d }
        a = 5;
        b = 10;
        c = 15;
        d = 20;
        result = calculate ( a b );
        print result;
        result = maximum ( c d );
        print result;
        counter = 0;
        while ( counter > 0 ) {
            increment ( );
            print counter
        };
        reset ( );
        print counter;
        halt
    }
    """
    
    print("=" * 80)
    print("SPL COMPILER - COMPLEX CODE GENERATION TEST")
    print("=" * 80)
    print("\nComplex Sample Program:")
    print(sample_code)
    print("=" * 80)
    
    # Phase 1: Lexer (Tokenization)
    print("\nPHASE 1: LEXER (Tokenization)")
    print("-" * 40)
    lexer = SPLLexer()
    tokens = list(lexer.tokenize(sample_code))
    print(f"OK: Generated {len(tokens)} tokens")
    
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
    
    analyzer = ScopeAnalyzer()
    success, errors = analyzer.analyze(parse_tree)
    
    if success:
        print("OK: Scope analysis passed!")
        print_semantic_errors(errors)
    else:
        print("FAIL: Scope analysis failed!")
        print_semantic_errors(errors)
        return False
    
    # Phase 4: Type Checker (Type Analysis)
    print("\nPHASE 4: TYPE CHECKER (Type Analysis)")
    print("-" * 40)
    
    type_success, type_errors = check_spl_types(parse_tree, analyzer.symbol_table)
    
    if type_success:
        print("OK: Type analysis passed!")
        print_type_errors(type_errors)
    else:
        print("FAIL: Type analysis failed!")
        print_type_errors(type_errors)
        return False
    
    # Phase 5: Code Generator (Intermediate Code Generation)
    print("\nPHASE 5: CODE GENERATOR (Intermediate Code Generation)")
    print("-" * 40)
    
    try:
        generated_code = generate_intermediate_code(parse_tree, analyzer.symbol_table, "complex_generated_code.txt")
        
        if generated_code:
            print("OK: Code generation successful!")
            print("\nGenerated Intermediate Code:")
            print("-" * 40)
            print(generated_code)
            print("-" * 40)
            print(f"Generated code saved to: complex_generated_code.txt")
        else:
            print("FAIL: Code generation failed!")
            return False
            
    except Exception as e:
        print(f"FAIL: Code generation error: {str(e)}")
        return False
    
    # Summary
    print("\n" + "=" * 80)
    print("COMPLEX CODE GENERATION SUMMARY")
    print("=" * 80)
    print("OK: Phase 1 (Lexer): Tokenization successful")
    print("OK: Phase 2 (Parser): Syntax analysis successful") 
    print("OK: Phase 3 (Scope Analyzer): Semantic analysis successful")
    print("OK: Phase 4 (Type Checker): Type analysis successful")
    print("OK: Phase 5 (Code Generator): Intermediate code generation successful")
    print("\nSUCCESS: ALL FIVE PHASES COMPLETED SUCCESSFULLY!")
    print("Your complex SPL program has been compiled to intermediate code.")
    print("=" * 80)
    
    return True

if __name__ == "__main__":
    test_complex_code_generation()
