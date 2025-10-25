from parser import parse_spl
from typechecker import type_check_spl

code = """
    glob {
}

proc {
}

func {
    testfunc(a) {
        local { }
        return a
    }
}

main {
    var { x y }
    x = 5;
    y = testfunc(x);
    print y;
    halt
}
"""

parse_tree = parse_spl(code)
if parse_tree:
    type_check_spl(parse_tree)