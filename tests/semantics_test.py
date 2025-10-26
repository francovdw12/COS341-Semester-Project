import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from parser import parse_spl
from semantics import analyze_semantics

code = r'''
glob { g1 g2 }
proc {
  show ( a ) {
    local { tmp }
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
  m = ( m plus g1 );
  show ( m );
  if ( m > 0 ) { print "ok" } else { halt };
  halt
}
'''

ast = parse_spl(code)
if ast is None:
    print("Parse failed")
else:
    sym, ids, errs = analyze_semantics(ast)
    print(sym.snapshot())
    if errs.items:
        print("\nErrors:")
        for e in errs.items:
            print(" -", e)
    else:
        print("\nNo semantic errors.")
