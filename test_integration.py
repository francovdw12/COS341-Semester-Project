# Integration Tests for SPL Compiler
from parser import parse_spl

def test(name, code, should_pass=True):
    result = parse_spl(code)
    success = (result is not None) == should_pass
    status = '[PASS]' if success else '[FAIL]'
    print(f'{status} {name}')
    return success

print('SPL Integration Tests')
print('='*50)

total = 0
passed = 0

# Test 1: Minimal program
total += 1
code1 = """glob { }
proc { }
func { }
main {
    var { }
    halt
}"""
if test('Minimal program', code1):
    passed += 1

# Test 2: With variables
total += 1
code2 = """glob { x }
proc { }
func { }
main {
    var { a }
    x = 10;
    a = 5;
    halt
}"""
if test('With variables', code2):
    passed += 1

# Test 3: With function
total += 1
code3 = """glob { }
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
if test('With function', code3):
    passed += 1

# Test 4: Invalid (should fail)
total += 1
code4 = """glob { }
proc { }
func { }
main {
    var { x }
    x = 5
    halt
}"""
if test('Invalid (no semicolon)', code4, should_pass=False):
    passed += 1

print('='*50)
print(f'Results: {passed}/{total} passed')
if passed == total:
    print('[OK] ALL TESTS PASSED')
