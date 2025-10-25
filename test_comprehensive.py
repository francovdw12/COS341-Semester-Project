"""
Comprehensive Test Suite for SPL Compiler
Tests lexer, parser, and type checker thoroughly
"""

import sys
import traceback
from lexer import SPLLexer
from parser import parse_spl
from typechecker import type_check_spl

class TestResult:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []

    def add_pass(self, test_name):
        self.passed += 1
        print(f"[PASS] {test_name}")

    def add_fail(self, test_name, error_msg=""):
        self.failed += 1
        self.errors.append(f"[FAIL] {test_name}: {error_msg}")
        print(f"[FAIL] {test_name}: {error_msg}")

    def summary(self):
        total = self.passed + self.failed
        print(f"\n{'='*60}")
        print(f"TEST SUMMARY: {self.passed}/{total} passed")
        if self.failed > 0:
            print(f"FAILED TESTS:")
            for error in self.errors:
                print(f"  {error}")
        print(f"{'='*60}")
        return self.failed == 0

def test_lexer_comprehensive():
    """Test lexer with comprehensive token coverage"""
    print("\n" + "="*60)
    print("TESTING LEXER COMPREHENSIVELY")
    print("="*60)
    
    result = TestResult()
    lexer = SPLLexer()
    
    # Test 1: All keywords
    try:
        keywords = "glob proc func main var local halt print while do until if else return"
        tokens = list(lexer.tokenize(keywords))
        expected_types = ['GLOB', 'PROC', 'FUNC', 'MAIN', 'VAR', 'LOCAL', 'HALT', 'PRINT', 
                         'WHILE', 'DO', 'UNTIL', 'IF', 'ELSE', 'RETURN']
        if len(tokens) == len(expected_types) and all(t.type == expected_types[i] for i, t in enumerate(tokens)):
            result.add_pass("All keywords recognized")
        else:
            result.add_fail("Keywords test", f"Expected {len(expected_types)} tokens, got {len(tokens)}")
    except Exception as e:
        result.add_fail("Keywords test", str(e))
    
    # Test 2: All operators
    try:
        operators = "= > eq or and plus minus mult div neg not"
        tokens = list(lexer.tokenize(operators))
        expected_types = ['ASSIGN', 'GT', 'EQ', 'OR', 'AND', 'PLUS', 'MINUS', 'MULT', 'DIV', 'NEG', 'NOT']
        if len(tokens) == len(expected_types) and all(t.type == expected_types[i] for i, t in enumerate(tokens)):
            result.add_pass("All operators recognized")
        else:
            result.add_fail("Operators test", f"Expected {len(expected_types)} tokens, got {len(tokens)}")
    except Exception as e:
        result.add_fail("Operators test", str(e))
    
    # Test 3: All punctuation
    try:
        punctuation = "( ) { } ;"
        tokens = list(lexer.tokenize(punctuation))
        expected_types = ['LPAREN', 'RPAREN', 'LBRACE', 'RBRACE', 'SEMICOLON']
        if len(tokens) == len(expected_types) and all(t.type == expected_types[i] for i, t in enumerate(tokens)):
            result.add_pass("All punctuation recognized")
        else:
            result.add_fail("Punctuation test", f"Expected {len(expected_types)} tokens, got {len(tokens)}")
    except Exception as e:
        result.add_fail("Punctuation test", str(e))
    
    # Test 4: Valid identifiers (user-defined names)
    try:
        identifiers = "x abc test123 variable1 func2"
        tokens = list(lexer.tokenize(identifiers))
        if len(tokens) == 5 and all(t.type == 'NAME' for t in tokens):
            result.add_pass("Valid identifiers recognized")
        else:
            result.add_fail("Identifiers test", f"Expected 5 NAME tokens, got {len(tokens)}")
    except Exception as e:
        result.add_fail("Identifiers test", str(e))
    
    # Test 5: Invalid identifiers (should not be recognized as keywords)
    try:
        invalid_identifiers = "X 123var _test"
        tokens = list(lexer.tokenize(invalid_identifiers))
        # These should not be recognized as valid NAME tokens
        if len(tokens) == 0:  # All should be ignored or cause errors
            result.add_pass("Invalid identifiers rejected")
        else:
            result.add_fail("Invalid identifiers test", f"Expected 0 tokens, got {len(tokens)}")
    except Exception as e:
        result.add_pass("Invalid identifiers rejected (exception as expected)")
    
    # Test 6: Numbers (0 and positive integers)
    try:
        numbers = "0 1 123 456 999"
        tokens = list(lexer.tokenize(numbers))
        expected_values = [0, 1, 123, 456, 999]
        if len(tokens) == 5 and all(t.type == 'NUMBER' and t.value == expected_values[i] for i, t in enumerate(tokens)):
            result.add_pass("Numbers recognized correctly")
        else:
            result.add_fail("Numbers test", f"Expected 5 NUMBER tokens with correct values")
    except Exception as e:
        result.add_fail("Numbers test", str(e))
    
    # Test 7: Strings (max 15 characters)
    try:
        strings = '"hello" "test123" "a" "123456789012345"'
        tokens = list(lexer.tokenize(strings))
        expected_values = ["hello", "test123", "a", "123456789012345"]
        if len(tokens) == 4 and all(t.type == 'STRING' and t.value == expected_values[i] for i, t in enumerate(tokens)):
            result.add_pass("Strings recognized correctly")
        else:
            result.add_fail("Strings test", f"Expected 4 STRING tokens with correct values")
    except Exception as e:
        result.add_fail("Strings test", str(e))
    
    # Test 8: Comments (should be ignored)
    try:
        code_with_comments = "x = 5; // This is a comment\ny = 10;"
        tokens = list(lexer.tokenize(code_with_comments))
        # Should have: x, =, 5, ;, y, =, 10, ;
        expected_count = 8
        if len(tokens) == expected_count:
            result.add_pass("Comments ignored correctly")
        else:
            result.add_fail("Comments test", f"Expected {expected_count} tokens, got {len(tokens)}")
    except Exception as e:
        result.add_fail("Comments test", str(e))
    
    # Test 9: Whitespace handling
    try:
        code = "   x   =   5   ;   "
        tokens = list(lexer.tokenize(code))
        expected_types = ['NAME', 'ASSIGN', 'NUMBER', 'SEMICOLON']
        if len(tokens) == 4 and all(t.type == expected_types[i] for i, t in enumerate(tokens)):
            result.add_pass("Whitespace handled correctly")
        else:
            result.add_fail("Whitespace test", f"Expected {len(expected_types)} tokens, got {len(tokens)}")
    except Exception as e:
        result.add_fail("Whitespace test", str(e))
    
    return result

def test_parser_comprehensive():
    """Test parser with comprehensive grammar coverage"""
    print("\n" + "="*60)
    print("TESTING PARSER COMPREHENSIVELY")
    print("="*60)
    
    result = TestResult()
    
    # Test 1: Minimal valid program
    try:
        code = """glob { }
proc { }
func { }
main {
    var { }
    halt
}"""
        ast = parse_spl(code)
        if ast is not None and ast[0] == 'SPL_PROG':
            result.add_pass("Minimal program parsed")
        else:
            result.add_fail("Minimal program", "Failed to parse or incorrect AST structure")
    except Exception as e:
        result.add_fail("Minimal program", str(e))
    
    # Test 2: Global variables
    try:
        code = """glob { x y z }
proc { }
func { }
main {
    var { }
    halt
}"""
        ast = parse_spl(code)
        if ast is not None:
            result.add_pass("Global variables parsed")
        else:
            result.add_fail("Global variables", "Failed to parse")
    except Exception as e:
        result.add_fail("Global variables", str(e))
    
    # Test 3: Procedure definition
    try:
        code = """glob { }
proc {
    testproc ( ) {
        local { }
        print "hello"
    }
}
func { }
main {
    var { }
    halt
}"""
        ast = parse_spl(code)
        if ast is not None:
            result.add_pass("Procedure definition parsed")
        else:
            result.add_fail("Procedure definition", "Failed to parse")
    except Exception as e:
        result.add_fail("Procedure definition", str(e))
    
    # Test 4: Function definition
    try:
        code = """glob { }
proc { }
func {
    add ( x y ) {
        local { result }
        result = ( x plus y );
        return result
    }
}
main {
    var { }
    halt
}"""
        ast = parse_spl(code)
        if ast is not None:
            result.add_pass("Function definition parsed")
        else:
            result.add_fail("Function definition", "Failed to parse")
    except Exception as e:
        result.add_fail("Function definition", str(e))
    
    # Test 5: Main program with variables
    try:
        code = """glob { }
proc { }
func { }
main {
    var { a b c }
    a = 5;
    b = 10;
    c = ( a plus b );
    halt
}"""
        ast = parse_spl(code)
        if ast is not None:
            result.add_pass("Main program with variables parsed")
        else:
            result.add_fail("Main program with variables", "Failed to parse")
    except Exception as e:
        result.add_fail("Main program with variables", str(e))
    
    # Test 6: Print statements
    try:
        code = """glob { }
proc { }
func { }
main {
    var { x }
    print "hello";
    print x;
    print 42;
    halt
}"""
        ast = parse_spl(code)
        if ast is not None:
            result.add_pass("Print statements parsed")
        else:
            result.add_fail("Print statements", "Failed to parse")
    except Exception as e:
        result.add_fail("Print statements", str(e))
    
    # Test 7: Assignment statements
    try:
        code = """glob { }
proc { }
func { }
main {
    var { x y }
    x = 5;
    y = ( x plus 10 );
    x = ( y mult 2 );
    halt
}"""
        ast = parse_spl(code)
        if ast is not None:
            result.add_pass("Assignment statements parsed")
        else:
            result.add_fail("Assignment statements", "Failed to parse")
    except Exception as e:
        result.add_fail("Assignment statements", str(e))
    
    # Test 8: Function calls
    try:
        code = """glob { }
proc { }
func {
    add ( x y ) {
        local { }
        return ( x plus y )
    }
}
main {
    var { result }
    result = add ( 5 10 );
    halt
}"""
        ast = parse_spl(code)
        if ast is not None:
            result.add_pass("Function calls parsed")
        else:
            result.add_fail("Function calls", "Failed to parse")
    except Exception as e:
        result.add_fail("Function calls", str(e))
    
    # Test 9: Procedure calls
    try:
        code = """glob { x }
proc {
    show ( ) {
        local { }
        print x
    }
}
func { }
main {
    var { }
    show ( );
    halt
}"""
        ast = parse_spl(code)
        if ast is not None:
            result.add_pass("Procedure calls parsed")
        else:
            result.add_fail("Procedure calls", "Failed to parse")
    except Exception as e:
        result.add_fail("Procedure calls", str(e))
    
    # Test 10: While loops
    try:
        code = """glob { }
proc { }
func { }
main {
    var { counter }
    counter = 5;
    while ( counter gt 0 ) {
        print counter;
        counter = ( counter minus 1 )
    };
    halt
}"""
        ast = parse_spl(code)
        if ast is not None:
            result.add_pass("While loops parsed")
        else:
            result.add_fail("While loops", "Failed to parse")
    except Exception as e:
        result.add_fail("While loops", str(e))
    
    # Test 11: Do-until loops
    try:
        code = """glob { }
proc { }
func { }
main {
    var { counter }
    counter = 5;
    do {
        print counter;
        counter = ( counter minus 1 )
    } until ( counter eq 0 );
    halt
}"""
        ast = parse_spl(code)
        if ast is not None:
            result.add_pass("Do-until loops parsed")
        else:
            result.add_fail("Do-until loops", "Failed to parse")
    except Exception as e:
        result.add_fail("Do-until loops", str(e))
    
    # Test 12: If statements
    try:
        code = """glob { }
proc { }
func { }
main {
    var { x }
    x = 10;
    if ( x gt 5 ) {
        print "x is greater than 5"
    };
    halt
}"""
        ast = parse_spl(code)
        if ast is not None:
            result.add_pass("If statements parsed")
        else:
            result.add_fail("If statements", "Failed to parse")
    except Exception as e:
        result.add_fail("If statements", str(e))
    
    # Test 13: If-else statements
    try:
        code = """glob { }
proc { }
func { }
main {
    var { x }
    x = 3;
    if ( x gt 5 ) {
        print "x is greater than 5"
    } else {
        print "x is not greater than 5"
    };
    halt
}"""
        ast = parse_spl(code)
        if ast is not None:
            result.add_pass("If-else statements parsed")
        else:
            result.add_fail("If-else statements", "Failed to parse")
    except Exception as e:
        result.add_fail("If-else statements", str(e))
    
    # Test 14: Complex expressions
    try:
        code = """glob { }
proc { }
func { }
main {
    var { result }
    result = ( ( 5 plus 3 ) mult ( 10 minus 2 ) );
    result = ( ( result eq 64 ) and ( result gt 0 ) );
    halt
}"""
        ast = parse_spl(code)
        if ast is not None:
            result.add_pass("Complex expressions parsed")
        else:
            result.add_fail("Complex expressions", "Failed to parse")
    except Exception as e:
        result.add_fail("Complex expressions", str(e))
    
    # Test 15: Unary operators
    try:
        code = """glob { }
proc { }
func { }
main {
    var { x y }
    x = ( neg 5 );
    y = ( not ( 5 eq 3 ) );
    halt
}"""
        ast = parse_spl(code)
        if ast is not None:
            result.add_pass("Unary operators parsed")
        else:
            result.add_fail("Unary operators", "Failed to parse")
    except Exception as e:
        result.add_fail("Unary operators", str(e))
    
    # Test 16: Invalid syntax (should fail)
    try:
        code = """glob { }
proc { }
func { }
main {
    var { x }
    x = 5  // Missing semicolon
    halt
}"""
        ast = parse_spl(code)
        if ast is None:
            result.add_pass("Invalid syntax correctly rejected")
        else:
            result.add_fail("Invalid syntax", "Should have failed to parse")
    except Exception as e:
        result.add_pass("Invalid syntax correctly rejected (exception as expected)")
    
    # Test 17: Complete complex program
    try:
        code = """glob { total }
proc {
    show ( ) {
        local { }
        print total
    }
}
func {
    multiply ( a b ) {
        local { result }
        result = ( a mult b );
        return result
    }
}
main {
    var { x y }
    x = 5;
    y = 10;
    total = multiply ( x y );
    show ( );
    halt
}"""
        ast = parse_spl(code)
        if ast is not None:
            result.add_pass("Complete complex program parsed")
        else:
            result.add_fail("Complete complex program", "Failed to parse")
    except Exception as e:
        result.add_fail("Complete complex program", str(e))
    
    return result

def test_typechecker_comprehensive():
    """Test type checker with comprehensive type checking"""
    print("\n" + "="*60)
    print("TESTING TYPE CHECKER COMPREHENSIVELY")
    print("="*60)
    
    result = TestResult()
    
    # Test 1: Valid program with correct types
    try:
        code = """glob { x }
proc { }
func {
    add ( a b ) {
        local { }
        return ( a plus b )
    }
}
main {
    var { y }
    x = 5;
    y = add ( x 10 );
    print y;
    halt
}"""
        ast = parse_spl(code)
        if ast is not None:
            success = type_check_spl(ast)
            if success:
                result.add_pass("Valid program type checked")
            else:
                result.add_fail("Valid program", "Type checking failed")
        else:
            result.add_fail("Valid program", "Parsing failed")
    except Exception as e:
        result.add_fail("Valid program", str(e))
    
    # Test 2: Undeclared variable
    try:
        code = """glob { }
proc { }
func { }
main {
    var { }
    x = 5;  // x is not declared
    halt
}"""
        ast = parse_spl(code)
        if ast is not None:
            success = type_check_spl(ast)
            if not success:  # Should fail
                result.add_pass("Undeclared variable correctly detected")
            else:
                result.add_fail("Undeclared variable", "Should have failed type checking")
        else:
            result.add_fail("Undeclared variable", "Parsing failed")
    except Exception as e:
        result.add_fail("Undeclared variable", str(e))
    
    # Test 3: Duplicate variable declaration
    try:
        code = """glob { x x }
proc { }
func { }
main {
    var { }
    halt
}"""
        ast = parse_spl(code)
        if ast is not None:
            success = type_check_spl(ast)
            if not success:  # Should fail
                result.add_pass("Duplicate variable correctly detected")
            else:
                result.add_fail("Duplicate variable", "Should have failed type checking")
        else:
            result.add_fail("Duplicate variable", "Parsing failed")
    except Exception as e:
        result.add_fail("Duplicate variable", str(e))
    
    # Test 4: Type mismatch in assignment
    try:
        code = """glob { x }
proc { }
func { }
main {
    var { }
    x = ( 5 eq 3 );  // Assigning boolean to numeric variable
    halt
}"""
        ast = parse_spl(code)
        if ast is not None:
            success = type_check_spl(ast)
            if not success:  # Should fail
                result.add_pass("Type mismatch correctly detected")
            else:
                result.add_fail("Type mismatch", "Should have failed type checking")
        else:
            result.add_fail("Type mismatch", "Parsing failed")
    except Exception as e:
        result.add_fail("Type mismatch", str(e))
    
    # Test 5: Invalid operator usage
    try:
        code = """glob { }
proc { }
func { }
main {
    var { x }
    x = ( 5 and 3 );  // Using boolean operator on numeric operands
    halt
}"""
        ast = parse_spl(code)
        if ast is not None:
            success = type_check_spl(ast)
            if not success:  # Should fail
                result.add_pass("Invalid operator usage correctly detected")
            else:
                result.add_fail("Invalid operator usage", "Should have failed type checking")
        else:
            result.add_fail("Invalid operator usage", "Parsing failed")
    except Exception as e:
        result.add_fail("Invalid operator usage", str(e))
    
    # Test 6: Function return type mismatch
    try:
        code = """glob { }
proc { }
func {
    test ( ) {
        local { }
        return ( 5 eq 3 )  // Returning boolean from function
    }
}
main {
    var { x }
    x = test ( );
    halt
}"""
        ast = parse_spl(code)
        if ast is not None:
            success = type_check_spl(ast)
            if not success:  # Should fail
                result.add_pass("Function return type mismatch correctly detected")
            else:
                result.add_fail("Function return type mismatch", "Should have failed type checking")
        else:
            result.add_fail("Function return type mismatch", "Parsing failed")
    except Exception as e:
        result.add_fail("Function return type mismatch", str(e))
    
    # Test 7: Undeclared function call
    try:
        code = """glob { }
proc { }
func { }
main {
    var { x }
    x = unknown ( 5 );  // Calling undeclared function
    halt
}"""
        ast = parse_spl(code)
        if ast is not None:
            success = type_check_spl(ast)
            if not success:  # Should fail
                result.add_pass("Undeclared function call correctly detected")
            else:
                result.add_fail("Undeclared function call", "Should have failed type checking")
        else:
            result.add_fail("Undeclared function call", "Parsing failed")
    except Exception as e:
        result.add_fail("Undeclared function call", str(e))
    
    # Test 8: Undeclared procedure call
    try:
        code = """glob { }
proc { }
func { }
main {
    var { }
    unknown ( );  // Calling undeclared procedure
    halt
}"""
        ast = parse_spl(code)
        if ast is not None:
            success = type_check_spl(ast)
            if not success:  # Should fail
                result.add_pass("Undeclared procedure call correctly detected")
            else:
                result.add_fail("Undeclared procedure call", "Should have failed type checking")
        else:
            result.add_fail("Undeclared procedure call", "Parsing failed")
    except Exception as e:
        result.add_fail("Undeclared procedure call", str(e))
    
    # Test 9: Complex valid program
    try:
        code = """glob { total }
proc {
    show ( ) {
        local { }
        print total
    }
}
func {
    multiply ( a b ) {
        local { result }
        result = ( a mult b );
        return result
    }
}
main {
    var { x y }
    x = 5;
    y = 10;
    total = multiply ( x y );
    show ( );
    halt
}"""
        ast = parse_spl(code)
        if ast is not None:
            success = type_check_spl(ast)
            if success:
                result.add_pass("Complex valid program type checked")
            else:
                result.add_fail("Complex valid program", "Type checking failed")
        else:
            result.add_fail("Complex valid program", "Parsing failed")
    except Exception as e:
        result.add_fail("Complex valid program", str(e))
    
    # Test 10: Scope testing
    try:
        code = """glob { x }
proc {
    test ( ) {
        local { }
        print x  // Should access global x
    }
}
func { }
main {
    var { }
    test ( );
    halt
}"""
        ast = parse_spl(code)
        if ast is not None:
            success = type_check_spl(ast)
            if success:
                result.add_pass("Scope testing passed")
            else:
                result.add_fail("Scope testing", "Type checking failed")
        else:
            result.add_fail("Scope testing", "Parsing failed")
    except Exception as e:
        result.add_fail("Scope testing", str(e))
    
    return result

def test_integration_comprehensive():
    """Test complete compiler pipeline"""
    print("\n" + "="*60)
    print("TESTING INTEGRATION COMPREHENSIVELY")
    print("="*60)
    
    result = TestResult()
    
    # Test 1: Complete valid program
    try:
        code = """glob { counter }
proc {
    decrement ( ) {
        local { }
        counter = ( counter minus 1 )
    }
}
func {
    factorial ( n ) {
        local { result }
        if ( n eq 0 ) {
            result = 1
        } else {
            result = ( n mult factorial ( ( n minus 1 ) ) )
        };
        return result
    }
}
main {
    var { n result }
    n = 5;
    counter = n;
    while ( counter gt 0 ) {
        print counter;
        decrement ( )
    };
    result = factorial ( n );
    print result;
    halt
}"""
        ast = parse_spl(code)
        if ast is not None:
            success = type_check_spl(ast)
            if success:
                result.add_pass("Complete valid program processed")
            else:
                result.add_fail("Complete valid program", "Type checking failed")
        else:
            result.add_fail("Complete valid program", "Parsing failed")
    except Exception as e:
        result.add_fail("Complete valid program", str(e))
    
    # Test 2: Error handling in pipeline
    try:
        code = """glob { }
proc { }
func { }
main {
    var { }
    x = 5;  // x not declared
    halt
}"""
        ast = parse_spl(code)
        if ast is not None:
            success = type_check_spl(ast)
            if not success:  # Should fail
                result.add_pass("Error handling in pipeline works")
            else:
                result.add_fail("Error handling", "Should have failed")
        else:
            result.add_fail("Error handling", "Parsing failed")
    except Exception as e:
        result.add_fail("Error handling", str(e))
    
    return result

def main():
    """Run all comprehensive tests"""
    print("COMPREHENSIVE SPL COMPILER TEST SUITE")
    print("="*60)
    
    # Run all test suites
    lexer_result = test_lexer_comprehensive()
    parser_result = test_parser_comprehensive()
    typechecker_result = test_typechecker_comprehensive()
    integration_result = test_integration_comprehensive()
    
    # Summary
    total_passed = lexer_result.passed + parser_result.passed + typechecker_result.passed + integration_result.passed
    total_failed = lexer_result.failed + parser_result.failed + typechecker_result.failed + integration_result.failed
    total_tests = total_passed + total_failed
    
    print(f"\n{'='*60}")
    print("FINAL SUMMARY")
    print(f"{'='*60}")
    print(f"Total tests: {total_tests}")
    print(f"Passed: {total_passed}")
    print(f"Failed: {total_failed}")
    
    if total_failed == 0:
        print("\n*** ALL TESTS PASSED! ***")
        print("The SPL compiler components are working correctly!")
    else:
        print(f"\n*** {total_failed} TESTS FAILED ***")
        print("Please review the failed tests above.")
    
    return total_failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
