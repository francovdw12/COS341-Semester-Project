"""
Test function calls
"""

from lexer import SPLLexer
from parser import parse_spl
from typechecker import type_check_spl

def test_function_calls():
    """Test function calls"""
    print("=== TESTING FUNCTION CALLS ===")
    
    # Test 1: Function definition and call
    code1 = """glob { }
proc { }
func {
    add ( x y ) {
        local { };
        return ( x plus y )
    }
}
main {
    var { result }
    result = add ( 5 10 );
    halt
}"""
    
    print("Test 1: Function definition and call")
    ast = parse_spl(code1)
    if ast:
        print("[PASS] Function definition and call parsed")
        success = type_check_spl(ast)
        if success:
            print("[PASS] Function definition and call type checked")
        else:
            print("[FAIL] Function definition and call type checking failed")
    else:
        print("[FAIL] Function definition and call parsing failed")
    
    # Test 2: Function with local variables
    code2 = """glob { }
proc { }
func {
    multiply ( a b ) {
        local { result }
        result = ( a mult b );
        return result
    }
}
main {
    var { x }
    x = multiply ( 3 4 );
    halt
}"""
    
    print("\nTest 2: Function with local variables")
    ast = parse_spl(code2)
    if ast:
        print("[PASS] Function with local variables parsed")
        success = type_check_spl(ast)
        if success:
            print("[PASS] Function with local variables type checked")
        else:
            print("[FAIL] Function with local variables type checking failed")
    else:
        print("[FAIL] Function with local variables parsing failed")
    
    # Test 3: Complex function with multiple instructions
    code3 = """glob { }
proc { }
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
    var { x }
    x = factorial ( 5 );
    halt
}"""
    
    print("\nTest 3: Complex function with multiple instructions")
    ast = parse_spl(code3)
    if ast:
        print("[PASS] Complex function parsed")
        success = type_check_spl(ast)
        if success:
            print("[PASS] Complex function type checked")
        else:
            print("[FAIL] Complex function type checking failed")
    else:
        print("[FAIL] Complex function parsing failed")

if __name__ == "__main__":
    test_function_calls()
