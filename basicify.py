# Converts our intermediate code to BASIC code that we're going to run using pcbasic.py library
from __future__ import annotations
import re
from typing import List, Tuple, Dict

# Label and jumpiung patterns
LABEL_RE = re.compile(r'^\s*REM\s+([A-Za-z_]\w*)\s*$')
GOTO_RE  = re.compile(r'\bGOTO\s+([A-Za-z_]\w*)\b')
THEN_RE  = re.compile(r'\bTHEN\s+([A-Za-z_]\w*)\b')

def intermediate_to_basic(inter_code: str, start: int = 10, step: int = 10) -> str:
    raw = [ln.rstrip() for ln in inter_code.splitlines() if ln.strip() != ""]
    numbered: List[Tuple[int, str]] = []
    label_to_num: Dict[str, int] = {}

    n = start
    for line in raw:
        numbered.append((n, line))
        m = LABEL_RE.match(line)
        if m:
            label_to_num[m.group(1)] = n
        n += step

    out_lines: List[str] = []
    for num, text in numbered:
        def repl_goto(m): return f"GOTO {label_to_num.get(m.group(1), m.group(1))}"
        def repl_then(m): return f"THEN {label_to_num.get(m.group(1), m.group(1))}"
        patched = GOTO_RE.sub(repl_goto, text)
        patched = THEN_RE.sub(repl_then, patched)
        out_lines.append(f"{num} {patched}")
    return "\n".join(out_lines)

def compile_spl_to_basic(spl_src: str, start: int = 10, step: int = 10) -> str:
    from parser import parse_spl
    from codegen_inline import generate_code
    ast = parse_spl(spl_src)
    if ast is None:
        raise ValueError("Parse failed; cannot generate BASIC.")
    inter = generate_code(ast)
    return intermediate_to_basic(inter, start=start, step=step)

# Simple CLI to read SPL and write BASIC
if __name__ == "__main__":
    import sys, pathlib
    if len(sys.argv) < 2:
        print("Usage: python basicify.py <input.spl> [output.bas]")
        sys.exit(1)

    inp = pathlib.Path(sys.argv[1])
    out = pathlib.Path(sys.argv[2]) if len(sys.argv) >= 3 else inp.with_suffix(".bas")

    src = inp.read_text(encoding="utf-8")
    basic = compile_spl_to_basic(src)
    out.write_text(basic + "\n", encoding="utf-8")
    print(f"Wrote {out}:\n")
    print(basic)