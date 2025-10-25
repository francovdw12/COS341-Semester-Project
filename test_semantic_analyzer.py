"""
Test suite for SPL Semantic Analyzer
Tests scope analysis, name-rule violations, and undeclared variable detection
"""

from parser import parse_spl
from semantic_analyzer import analyze_spl_semantics, print_semantic_errors


def test_semantic_analysis(name, code, should_pass=True, expected_errors=None):
    """Test semantic analysis with expected results"""
    print(f"\n{'='*60}")
    print(f"Test: {name}")
    print(f"{'='*60}")
    print(f"Code:\n{code}")
    
    # Parse the code
    ast = parse_spl(code)
    if ast is None:
        print("FAIL: Parsing failed")
        return False
    
    # Analyze semantics
    success, errors = analyze_spl_semantics(ast)
    
    print(f"\nSemantic Analysis Results:")
    print_semantic_errors(errors)
    
    # Check if results match expectations
    if should_pass:
        if success and len(errors) == 0:
            print("PASS: Test PASSED - No semantic errors found")
            return True
        else:
            print(f"FAIL: Test FAILED - Expected no errors, but found {len(errors)}")
            return False
    else:
        if not success and len(errors) > 0:
            if expected_errors:
                # Check if we got the expected error types
                error_types = [e.error_type for e in errors]
                if all(expected_error in error_types for expected_error in expected_errors):
                    print("PASS: Test PASSED - Found expected semantic errors")
                    return True
                else:
                    print(f"FAIL: Test FAILED - Expected errors {expected_errors}, got {error_types}")
                    return False
            else:
                print("PASS: Test PASSED - Found semantic errors as expected")
                return True
        else:
            print(f"FAIL: Test FAILED - Expected errors, but found none")
            return False


def run_all_tests():
    """Run all semantic analysis tests"""
    print("SPL SEMANTIC ANALYZER TEST SUITE")
    print("="*80)
    
    total_tests = 0
    passed_tests = 0
    
    # Test 1: Valid program with no errors
    total_tests += 1
    code1 = """glob { x y }
proc { }
func { }
main {
    var { a }
    x = 10;
    y = 20;
    a = 5;
    halt
}"""
    if test_semantic_analysis("Valid program", code1, should_pass=True):
        passed_tests += 1
    
    # Test 2: Duplicate variable names in same scope (should fail)
    total_tests += 1
    code2 = """glob { x x }
proc { }
func { }
main {
    var { a }
    halt
}"""
    if test_semantic_analysis("Duplicate global variables", code2, should_pass=False, 
                             expected_errors=["NAME_RULE_VIOLATION"]):
        passed_tests += 1
    
    # Test 3: Duplicate local variables in main (should fail)
    total_tests += 1
    code3 = """glob { }
proc { }
func { }
main {
    var { a a }
    halt
}"""
    if test_semantic_analysis("Duplicate local variables in main", code3, should_pass=False,
                             expected_errors=["NAME_RULE_VIOLATION"]):
        passed_tests += 1
    
    # Test 4: Undeclared variable (should fail)
    total_tests += 1
    code4 = """glob { }
proc { }
func { }
main {
    var { a }
    b = 10;
    halt
}"""
    if test_semantic_analysis("Undeclared variable", code4, should_pass=False,
                             expected_errors=["UNDECLARED_VARIABLE"]):
        passed_tests += 1
    
    # Test 5: Valid function with parameters
    total_tests += 1
    code5 = """glob { }
proc { }
func {
    add ( x y ) {
        local { result }
        result = ( x plus y );
        return result
    }
}
main {
    var { z }
    z = add ( 5 10 );
    halt
}"""
    if test_semantic_analysis("Valid function with parameters", code5, should_pass=True):
        passed_tests += 1
    
    # Test 6: Duplicate function names (should fail)
    total_tests += 1
    code6 = """glob { }
proc { }
func {
    add ( x y ) {
        local { result }
        result = ( x plus y );
        return result
    }
    add ( a b ) {
        local { result }
        result = ( a mult b );
        return result
    }
}
main {
    var { z }
    halt
}"""
    if test_semantic_analysis("Duplicate function names", code6, should_pass=False,
                             expected_errors=["NAME_RULE_VIOLATION"]):
        passed_tests += 1
    
    # Test 7: Variable name conflicts with function name (should fail)
    total_tests += 1
    code7 = """glob { add }
proc { }
func {
    add ( x y ) {
        local { result }
        result = ( x plus y );
        return result
    }
}
main {
    var { z }
    halt
}"""
    if test_semantic_analysis("Variable name conflicts with function name", code7, should_pass=False,
                             expected_errors=["NAME_RULE_VIOLATION"]):
        passed_tests += 1
    
    # Test 8: Valid procedure
    total_tests += 1
    code8 = """glob { total }
proc {
    show ( ) {
        local { }
        print total
    }
}
func { }
main {
    var { x }
    x = 5;
    show ( );
    halt
}"""
    if test_semantic_analysis("Valid procedure", code8, should_pass=True):
        passed_tests += 1
    
    # Test 9: Duplicate procedure names (should fail)
    total_tests += 1
    code9 = """glob { }
proc {
    show ( ) {
        local { }
        print "hello"
    }
    show ( ) {
        local { }
        print "world"
    }
}
func { }
main {
    var { }
    halt
}"""
    if test_semantic_analysis("Duplicate procedure names", code9, should_pass=False,
                             expected_errors=["NAME_RULE_VIOLATION"]):
        passed_tests += 1
    
    # Test 10: Complex valid program
    total_tests += 1
    code10 = """glob { total }
proc {
    show ( ) {
        local { }
        print total
    }
}
func {
    multiply ( a b ) {
        local { }
        return ( a mult b )
    }
}
main {
    var { x }
    x = 5;
    total = multiply ( x 10 );
    show ( );
    halt
}"""
    if test_semantic_analysis("Complex valid program", code10, should_pass=True):
        passed_tests += 1
    
    # Test 11: Undeclared procedure call (should fail)
    total_tests += 1
    code11 = """glob { }
proc { }
func { }
main {
    var { }
    unknown ( );
    halt
}"""
    if test_semantic_analysis("Undeclared procedure call", code11, should_pass=False,
                             expected_errors=["UNDECLARED_VARIABLE"]):
        passed_tests += 1
    
    # Test 12: Undeclared function call (should fail)
    total_tests += 1
    code12 = """glob { }
proc { }
func { }
main {
    var { z }
    z = unknown ( 5 10 );
    halt
}"""
    if test_semantic_analysis("Undeclared function call", code12, should_pass=False,
                             expected_errors=["UNDECLARED_VARIABLE"]):
        passed_tests += 1
    
    # Print final results
    print(f"\n{'='*80}")
    print(f"SEMANTIC ANALYSIS TEST RESULTS")
    print(f"{'='*80}")
    print(f"Total tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    
    if passed_tests == total_tests:
        print("SUCCESS: ALL TESTS PASSED!")
        return True
    else:
        print("FAILURE: SOME TESTS FAILED")
        return False


if __name__ == "__main__":
    run_all_tests()
