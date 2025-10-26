import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from parser import parse_spl
from typespec import analyze_types_spec

TOTAL = 0
PASSED = 0

def run(name: str, program: str, should_type_ok: bool = True):
    """Run one test. Negative tests must PARSE, then fail typing."""
    global TOTAL, PASSED
    TOTAL += 1
    ast = parse_spl(program)
    if ast is None:
        print(f"[FAIL] {name}  — parse failed (wanted {'type OK' if should_type_ok else 'type FAIL'})")
        return
    errors = analyze_types_spec(ast)
    ok = (len(errors) == 0) == should_type_ok
    lab = 'PASS' if ok else 'FAIL'
    print(f"[{lab}] {name}")
    if not ok:
        print("  Program:")
        print(program)
        print("  Type errors:")
        if errors:
            for e in errors:
                print("   -", e)
        else:
            print("   - (no type errors reported)")
    PASSED += 1 if ok else 0


# --------------------------------------------------------------------
# Passing tests
# --------------------------------------------------------------------

# 1) Minimal program
run("Minimal OK", r"""
glob { }
proc { }
func { }
main {
  var { }
  halt
}
""", should_type_ok=True)

# 2) Numeric vars and arithmetic + print string
run("Arithmetic & print string OK", r"""
glob { x }
proc { }
func { }
main {
  var { a }
  x = 10;
  a = ( x plus 5 );
  print "ok";
  halt
}
""", should_type_ok=True)

# 3) Proc + Func + proper arity, types OK
run("Proc & Func arity OK", r"""
glob { }
proc {
  p ( a ) {
    local { }
    print a
  }
}
func {
  add ( x y ) {
    local { r }
    r = ( x plus y );
    return r
  }
}
main {
  var { m }
  m = add ( 1 2 );
  p ( m );
  halt
}
""", should_type_ok=True)

# 4) Boolean conditions in if/while/do-until
run("Boolean conditions OK", r"""
glob { }
proc { }
func { }
main {
  var { x }
  x = 3;
  if ( x > 0 ) { print "pos" } else { halt };
  while ( x > 0 ) { x = ( x minus 1 ) };
  do { x = ( x minus 1 ) } until ( x eq 0 );
  halt
}
""", should_type_ok=True)

# 5) AND/OR on booleans
run("Boolean ops AND/OR OK", r"""
glob { }
proc { }
func { }
main {
  var { }
  if ( ( 1 eq 1 ) and ( 2 eq 2 ) ) { print "ok" } else { halt };
  if ( ( 3 eq 4 ) or ( 5 eq 5 ) ) { print "maybe" } else { halt };
  halt
}
""", should_type_ok=True)

# 6) Three-arg function call
run("3-arg function OK", r"""
glob { }
proc { }
func {
  f ( a b c ) {
    local { r }
    r = ( ( a plus b ) plus c );
    return r
  }
}
main {
  var { x }
  x = f ( 1 2 3 );
  halt
}
""", should_type_ok=True)

# --------------------------------------------------------------------
# Failing tests (must parse, then fail typing)
# --------------------------------------------------------------------

# A) While with numeric condition (expects boolean)
run("While with numeric condition (FAIL)", r"""
glob { }
proc { }
func { }
main {
  var { }
  while 1 { halt };
  halt
}
""", should_type_ok=False)

# B) If with numeric condition (expects boolean)
run("If with numeric condition (FAIL)", r"""
glob { }
proc { }
func { }
main {
  var { }
  if 1 { halt };
  halt
}
""", should_type_ok=False)

# C) Assign boolean to numeric var
run("Assign boolean to var (FAIL)", r"""
glob { x }
proc { }
func { }
main {
  var { }
  x = ( 1 eq 2 );
  halt
}
""", should_type_ok=False)

# D) Boolean op AND on numeric terms (both sides numeric)
run("Boolean op on numeric (FAIL)", r"""
glob { x }
proc { }
func { }
main {
  var { }
  x = ( 1 and 2 );
  halt
}
""", should_type_ok=False)

# E) Comparison '>' with boolean left term
run("Comparison on boolean term (FAIL)", r"""
glob { }
proc { }
func { }
main {
  var { }
  if ( ( 1 eq 1 ) > 0 ) { halt } else { halt };
  halt
}
""", should_type_ok=False)

# F) Call a function as a procedure
run("Call function as procedure (FAIL)", r"""
glob { }
proc { }
func {
  f ( a ) {
    local { }
    a = ( a plus 1 );
    return a
  }
}
main {
  var { }
  f ( 1 );
  halt
}
""", should_type_ok=False)

# G) Assign result of a procedure
run("Assign result of procedure (FAIL)", r"""
glob { }
proc {
  p ( a ) {
    local { }
    print a
  }
}
func { }
main {
  var { x }
  x = p ( 1 );
  halt
}
""", should_type_ok=False)

# H) NAME not typeless: call a variable like a procedure
run("NAME not typeless (var called like proc) (FAIL)", r"""
glob { q }
proc { }
func { }
main {
  var { }
  q ( );
  halt
}
""", should_type_ok=False)

# I) Procedure arity mismatch (expects 1, got 0)
run("Procedure arity mismatch (FAIL)", r"""
glob { }
proc {
  show ( a ) {
    local { }
    print a
  }
}
func { }
main {
  var { }
  show ( );
  halt
}
""", should_type_ok=False)

# J) Function arity mismatch (expects 2, got 1)
run("Function arity mismatch (FAIL)", r"""
glob { }
proc { }
func {
  add ( x y ) {
    local { r }
    r = ( x plus y );
    return r
  }
}
main {
  var { z }
  z = add ( 1 );
  halt
}
""", should_type_ok=False)

# K) 'not' applied to numeric
run("'not' on numeric (FAIL)", r"""
glob { }
proc { }
func { }
main {
  var { }
  if ( not 1 ) { halt } else { halt };
  halt
}
""", should_type_ok=False)

# L) 'neg' applied to boolean
run("'neg' on boolean (FAIL)", r"""
glob { x }
proc { }
func { }
main {
  var { }
  x = ( neg ( 1 eq 2 ) );
  halt
}
""", should_type_ok=False)

# M) Bad boolean operands: numeric AND boolean
run("Bad boolean operands (FAIL)", r"""
glob { }
proc { }
func { }
main {
  var { }
  if ( 1 and ( 2 eq 2 ) ) { halt } else { halt };
  halt
}
""", should_type_ok=False)

# N) do-until with numeric condition (expects boolean)
run("do-until with numeric condition (FAIL)", r"""
glob { }
proc { }
func { }
main {
  var { }
  do { print "loop" } until 1;
  halt
}
""", should_type_ok=False)

run("Boolean conditions OK", r"""
    glob { maxval }
    proc { }
    func {
        findmaximum ( x y ) {
            local { result }
            if ( x > y ) {
            result = x
            } else {
            result = y
            };
            return result
        }
    }

    main {
        var { a b }
        a = 7;
        b = 12;
        maxval = findmaximum ( a b );
        print maxval;
        halt
    }
""", should_type_ok=True)

print("="*60)
print(f"Results: {PASSED}/{TOTAL} tests passed")
if PASSED == TOTAL:
    print("[OK] ALL TESTS PASSED")
else:
    print("[!] Some tests failed – see details above.")
