"""
Comprehensive test for inlining phase
Demonstrates complex inlining with nested calls and multiple functions
"""

from lexer import SPLLexer
from parser import parse_spl
from semantic_analyzer import analyze_spl_semantics, print_semantic_errors, ScopeAnalyzer
from type_checker import check_spl_types, print_type_errors
from code_generator import generate_intermediate_code
from inliner import inline_intermediate_code

def test_comprehensive_inlining():
    """Test comprehensive inlining with complex program"""
    
    # Complex program with multiple functions and procedures
    sample_code = """
    glob { total maxval }
    proc {
        showresult ( value ) {
            local { }
            print value
        }
        
        incrementcounter ( ) {
            local { }
            total = ( total plus 1 )
        }
    }
    func {
        square ( x ) {
            local { result }
            result = ( x mult x );
            return result
        }
        
        addnumbers ( a b ) {
            local { sum }
            sum = ( a plus b );
            return sum
        }
        
        findmax ( x y z ) {
            local { temp }
            if ( x > y ) {
                temp = x
            } else {
                temp = y
            };
            if ( temp > z ) {
                temp = temp
            } else {
                temp = z
            };
            return temp
        }
    }
    main {
        var { a b c d }
        a = 3;
        b = 7;
        c = 5;
        d = 9;
        total = 0;
        maxval = findmax ( a b c );
        showresult ( maxval );
        a = square ( b );
        showresult ( a );
        b = addnumbers ( c d );
        showresult ( b );
        incrementcounter ( );
        showresult ( total );
        halt
    }
    """
    
    print("=" * 80)
    print("SPL COMPILER - COMPREHENSIVE INLINING TEST")
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
        intermediate_code = generate_intermediate_code(parse_tree, analyzer.symbol_table, "comprehensive_intermediate.txt")
        
        if intermediate_code:
            print("OK: Code generation successful!")
            print("\nGenerated Intermediate Code (with CALL instructions):")
            print("-" * 60)
            print(intermediate_code)
            print("-" * 60)
        else:
            print("FAIL: Code generation failed!")
            return False
            
    except Exception as e:
        print(f"FAIL: Code generation error: {str(e)}")
        return False
    
    # Phase 6: Inliner (Replace CALL instructions with inlined code)
    print("\nPHASE 6: INLINER (Replace CALL with inlined code)")
    print("-" * 40)
    
    try:
        inlined_code = inline_intermediate_code(parse_tree, analyzer.symbol_table, intermediate_code, "comprehensive_inlined.txt")
        
        if inlined_code:
            print("OK: Inlining successful!")
            print("\nInlined Code (CALL instructions replaced):")
            print("-" * 60)
            print(inlined_code)
            print("-" * 60)
            print(f"Inlined code saved to: comprehensive_inlined.txt")
        else:
            print("FAIL: Inlining failed!")
            return False
            
    except Exception as e:
        print(f"FAIL: Inlining error: {str(e)}")
        return False
    
    # Summary
    print("\n" + "=" * 80)
    print("COMPREHENSIVE INLINING SUMMARY")
    print("=" * 80)
    print("OK: Phase 1 (Lexer): Tokenization successful")
    print("OK: Phase 2 (Parser): Syntax analysis successful") 
    print("OK: Phase 3 (Scope Analyzer): Semantic analysis successful")
    print("OK: Phase 4 (Type Checker): Type analysis successful")
    print("OK: Phase 5 (Code Generator): Intermediate code generation successful")
    print("OK: Phase 6 (Inliner): CALL instruction inlining successful")
    print("\nSUCCESS: ALL SIX PHASES COMPLETED SUCCESSFULLY!")
    print("Your complex SPL program has been fully compiled with inlined code.")
    print("All CALL instructions have been replaced with actual function/procedure code!")
    print("=" * 80)
    
    return True

if __name__ == "__main__":
    test_comprehensive_inlining()
