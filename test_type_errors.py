"""
Test program to demonstrate enhanced type error reporting
"""

from lexer import SPLLexer
from parser import parse_spl
from semantic_analyzer import analyze_spl_semantics, print_semantic_errors, ScopeAnalyzer
from type_checker import check_spl_types, print_type_errors

def test_type_errors():
    """Test program with multiple type errors to demonstrate enhanced error reporting"""
    
    # Program with various type errors
    sample_code = """
    glob { z }
    proc { }
    func {
        foo ( a b ) {
            local { result }
            result = ( neg ( a eq b ) );
            return result
        }
        
        badfunc ( x ) {
            local { temp }
            temp = ( x plus ( neg ( x eq 5 ) ) );
            return temp
        }
    }
    main {
        var { p q r }
        p = 1;
        q = 1;
        r = ( p plus ( neg q ) );
        if ( p eq q ) {
            print p
        } else {
            print q
        };
        halt
    }
    """
    
    print("=" * 80)
    print("SPL COMPILER - TYPE ERROR TESTING")
    print("=" * 80)
    print("\nSample Program with Type Errors:")
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
    
    print("\n" + "=" * 80)
    print("ENHANCED TYPE ERROR REPORTING DEMONSTRATION")
    print("=" * 80)
    print("The type checker now provides detailed information about:")
    print("• Location: Where the error occurred (function, statement, etc.)")
    print("• Context: What was being checked (assignment, condition, etc.)")
    print("• Node ID: For debugging and tracing")
    print("• Specific error messages with expected vs actual types")
    print("=" * 80)
    
    return type_success

if __name__ == "__main__":
    test_type_errors()
