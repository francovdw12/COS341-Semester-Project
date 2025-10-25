# basicify_test.py
# Tests for Final Phase: Intermediate (unnumbered) --> Executable BASIC (line-numbered)
#
# It validates:
#   - Every non-empty intermediate line gets a BASIC line number.
#   - Numbers progress by the chosen step (default 10).
#   - Each "REM Label" line's number is used to replace
#       * every "THEN Label"
#       * every "GOTO Label"
#   - No label names remain after transformation (only numeric line targets).
#
# The tests compile SPL -> intermediate -> BASIC, and also call compile_spl_to_basic.

import re
from parser import parse_spl
from codegen import generate_code
from basicify import intermediate_to_basic, compile_spl_to_basic

TOTAL = 0
PASSED = 0

LABEL_RE = re.compile(r'^\s*REM\s+([A-Za-z_]\w*)\s*$')
THEN_L_RE = re.compile(r'\bTHEN\s+([A-Za-z_]\w*)\b')
GOTO_L_RE = re.compile(r'\bGOTO\s+([A-Za-z_]\w*)\b')
THEN_N_RE = re.compile(r'\bTHEN\s+(\d+)\b')
GOTO_N_RE = re.compile(r'\bGOTO\s+(\d+)\b')

def verify_transformation(inter_code: str, basic_code: str, start=10, step=10) -> None:
    """Raise AssertionError if the mapping THEN/GOTO label -> number is wrong."""
    raw = [ln.rstrip() for ln in inter_code.splitlines() if ln.strip() != ""]
    bas = [ln.rstrip() for ln in basic_code.splitlines() if ln.strip() != ""]

    assert len(raw) == len(bas), "Line count mismatch"

    # Build numbering
    line_nums = [start + i * step for i in range(len(raw))]

    # Map 'Label' -> line number where 'REM Label' occurs
    label_to_num = {}
    for ln, txt in zip(line_nums, raw):
        m = LABEL_RE.match(txt)
        if m:
            label_to_num[m.group(1)] = ln

    # Check each line
    for i, (ln, raw_txt, bas_txt) in enumerate(zip(line_nums, raw, bas)):
        # 1) Correct prefix number
        assert bas_txt.startswith(f"{ln} "), f"Wrong BASIC line number at line {i+1}: {bas_txt!r}"

        # 2) For each THEN/GOTO label in the raw line, BASIC must contain the matching number
        expect_thens = [label_to_num[lbl] for lbl in THEN_L_RE.findall(raw_txt)]
        expect_gotos = [label_to_num[lbl] for lbl in GOTO_L_RE.findall(raw_txt)]

        found_thens = [int(n) for n in THEN_N_RE.findall(bas_txt)]
        found_gotos = [int(n) for n in GOTO_N_RE.findall(bas_txt)]

        for need in expect_thens:
            assert need in found_thens, f"Missing THEN {need} in BASIC: {bas_txt!r}"
        for need in expect_gotos:
            assert need in found_gotos, f"Missing GOTO {need} in BASIC: {bas_txt!r}"

        # 3) Ensure no leftover THEN/GOTO with labels (only digits allowed now)
        assert not THEN_L_RE.search(bas_txt), f"Leftover THEN <label> in BASIC: {bas_txt!r}"
        assert not GOTO_L_RE.search(bas_txt), f"Leftover GOTO <label> in BASIC: {bas_txt!r}"

def run(name: str, spl_program: str, start=10, step=10):
    global TOTAL, PASSED
    TOTAL += 1
    try:
        ast = parse_spl(spl_program)
        if ast is None:
            raise AssertionError("Parse failed")

        inter = generate_code(ast)
        basic_a = intermediate_to_basic(inter, start=start, step=step)
        basic_b = compile_spl_to_basic(spl_program, start=start, step=step)
        # Both routes must agree
        assert basic_a == basic_b, "basicify mismatch between two entry-points"

        # Verify mapping
        verify_transformation(inter, basic_a, start=start, step=step)

        print(f"[PASS] {name}")
        PASSED += 1
    except AssertionError as e:
        print(f"[FAIL] {name}: {e}")
        print("---- SPL ----")
        print(spl_program)
        print("---- Intermediate ----")
        try:
            print(inter)
        except Exception:
            print("(no intermediate – earlier failure)")
        print("---- BASIC ----")
        try:
            print(basic_a)
        except Exception:
            print("(no BASIC – earlier failure)")

# --------------------------------------------------------------------
# Tests
# --------------------------------------------------------------------

# 1) Minimal program -> STOP (single line)
run("Minimal → STOP", r"""
glob { }
proc { }
func { }
main {
  var { }
  halt
}
""")

# 2) if-else (ensures THEN/GOTO rewritten; last instr no semicolon)
run("if-else", r"""
glob { }
proc { }
func { }
main {
  var { }
  if ( 1 eq 1 ) { print "T" } else { print "F" };
  halt
}
""")

# 3) if (no else)
run("if w/out else", r"""
glob { }
proc { }
func { }
main {
  var { }
  if ( 2 > 1 ) { print "ok" };
  halt
}
""")

# 4) while loop
run("while loop", r"""
glob { }
proc { }
func { }
main {
  var { x }
  x = 3;
  while ( x > 0 ) { x = ( x minus 1 ) };
  halt
}
""")

# 5) do-until loop
run("do-until loop", r"""
glob { }
proc { }
func { }
main {
  var { x }
  x = 2;
  do { x = ( x minus 1 ) } until ( x eq 0 );
  halt
}
""")

# 6) boolean AND cascading
run("boolean AND", r"""
glob { }
proc { }
func { }
main {
  var { }
  if ( ( 1 eq 1 ) and ( 2 eq 3 ) ) { print "yes" } else { print "no" };
  halt
}
""")

# 7) boolean OR cascading
run("boolean OR", r"""
glob { }
proc { }
func { }
main {
  var { }
  if ( ( 1 eq 0 ) or ( 2 eq 2 ) ) { print "yes" } else { print "no" };
  halt
}
""")

# 8) NOT (implemented by swapped branches in cond handling)
run("boolean NOT", r"""
glob { }
proc { }
func { }
main {
  var { }
  if ( not ( 1 eq 1 ) ) { print "yes" } else { print "no" };
  halt
}
""")

# 9) arithmetic + function call
run("function call + arithmetic", r"""
glob { }
proc { }
func {
  add ( a b ) {
    local { r }
    r = ( a plus b );
    return r
  }
}
main {
  var { z }
  z = add ( 1 2 );
  print z;
  halt
}
""")

# 10) Full example: findmaximum
run("findmaximum example", r"""
glob { maxval }
proc { }
func {
  findmaximum ( x y ) {
    local { result }
    if ( x > y ) { result = x } else { result = y };
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
""")

# 11) Custom numbering (start 100, step 20)
run("Custom numbering 100..20", r"""
glob { }
proc { }
func { }
main {
  var { x }
  x = 1;
  if ( x > 0 ) { print "p" } else { print "q" };
  halt
}
""", start=100, step=20)

print("="*60)
print(f"Results: {PASSED}/{TOTAL} tests passed")
if PASSED == TOTAL:
    print("[OK] ALL TESTS PASSED")
else:
    print("[!] Some tests failed – see details above.")
