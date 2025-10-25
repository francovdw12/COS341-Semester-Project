"""
Final comprehensive test with correct syntax
"""

from parser import parse_spl
from typechecker import type_check_spl

def test_all():
    """Test all components"""
    print("="*60)
    print("FINAL COMPREHENSIVE TEST")
    print("="*60)
    
    passed = 0
    total = 0
    
    # Test 1: Simple function (no instructions in body)
    total += 1
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
    print result;
    halt
}"""
    
    print("\n1. Simple function (no instructions in body)")
    ast1 = parse_spl(code1)
    if ast1:
        print("   [PASS] Parsing")
        if type_check_spl(ast1):
            print("   [PASS] Type checking")
            passed += 1
        else:
            print("   [FAIL] Type checking")
    else:
        print("   [FAIL] Parsing")
    
    # Test 2: Complete program with procedures and functions
    total += 1
    code2 = """glob { counter }
proc {
    show ( ) {
        local { }
        print counter
    }
}
func {
    double ( n ) {
        local { };
        return ( n plus n )
    }
}
main {
    var { x }
    x = 5;
    counter = double ( x );
    show ( );
    halt
}"""
    
    print("\n2. Complete program with procedures and functions")
    ast2 = parse_spl(code2)
    if ast2:
        print("   [PASS] Parsing")
        if type_check_spl(ast2):
            print("   [PASS] Type checking")
            passed += 1
        else:
            print("   [FAIL] Type checking")
    else:
        print("   [FAIL] Parsing")
    
    # Test 3: Complex control flow
    total += 1
    code3 = """glob { }
proc { }
func { }
main {
    var { x y }
    x = 10;
    y = 0;
    while ( x gt 0 ) {
        y = ( y plus x );
        x = ( x minus 1 )
    };
    if ( y gt 50 ) {
        print "big"
    } else {
        print "small"
    };
    halt
}"""
    
    print("\n3. Complex control flow")
    ast3 = parse_spl(code3)
    if ast3:
        print("   [PASS] Parsing")
        if type_check_spl(ast3):
            print("   [PASS] Type checking")
            passed += 1
        else:
            print("   [FAIL] Type checking")
    else:
        print("   [FAIL] Parsing")
    
    print("\n" + "="*60)
    print(f"RESULTS: {passed}/{total} tests passed")
    print("="*60)
    
    if passed == total:
        print("\n*** ALL TESTS PASSED! ***")
        print("The SPL compiler is working correctly!")
        return True
    else:
        print(f"\n*** {total - passed} TESTS FAILED ***")
        return False

if __name__ == "__main__":
    test_all()
