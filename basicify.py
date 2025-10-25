# basicify.py
# Final Phase: Intermediate → Executable BASIC (line-numbered)
#
# - Numbers every non-empty line (default: 10, 20, 30, ...)
# - Collects label locations from lines of the form:   REM <Label>
# - Rewrites:  GOTO <Label>  →  GOTO <LineNumber>
#              THEN <Label>  →  THEN <LineNumber>
#
# Public API:
#   intermediate_to_basic(inter_code: str, start=10, step=10) -> str
#   compile_spl_to_basic(spl_src: str, start=10, step=10) -> str
#
# CLI:
#   python basicify.py <input.spl> [output.bas]
#
# Assumes your earlier phases (parser + codegen) are in place.

from __future__ import annotations
import re
from typing import List, Tuple, Dict, Optional

# --- Regexes for labels and jumps ---
LABEL_RE = re.compile(r'^\s*REM\s+([A-Za-z_]\w*)\s*$')       # whole label line: REM Lx
GOTO_RE  = re.compile(r'\bGOTO\s+([A-Za-z_]\w*)\b')          # GOTO Lx
THEN_RE  = re.compile(r'\bTHEN\s+([A-Za-z_]\w*)\b')          # THEN Lx

def intermediate_to_basic(inter_code: str, start: int = 10, step: int = 10) -> str:
    """
    Convert un-numbered intermediate code (our IF/GOTO/REM/PRINT/STOP form)
    into line-numbered BASIC code with label references resolved.
    """
    # 1) Keep non-empty lines, strip right whitespace
    raw_lines: List[str] = [ln.rstrip() for ln in inter_code.splitlines() if ln.strip() != ""]

    # 2) Assign line numbers and discover label locations
    numbered: List[Tuple[int, str]] = []
    label_to_num: Dict[str, int] = {}
    n = start
    for line in raw_lines:
        numbered.append((n, line))
        m = LABEL_RE.match(line)
        if m:
            label_to_num[m.group(1)] = n
        n += step

    # 3) Patch THEN/GOTO label references to their numeric line numbers
    out_lines: List[str] = []
    for num, text in numbered:
        def repl_goto(m: re.Match) -> str:
            lab = m.group(1)
            return f"GOTO {label_to_num.get(lab, lab)}"
        def repl_then(m: re.Match) -> str:
            lab = m.group(1)
            return f"THEN {label_to_num.get(lab, lab)}"
        patched = GOTO_RE.sub(repl_goto, text)
        patched = THEN_RE.sub(repl_then, patched)
        out_lines.append(f"{num} {patched}")

    return "\n".join(out_lines)

# --- Convenience: directly compile SPL → BASIC using your parser + codegen ---

def compile_spl_to_basic(spl_src: str, start: int = 10, step: int = 10) -> str:
    """Parse SPL, generate intermediate code, then BASIC-ify with line numbers."""
    from parser import parse_spl
    from codegen import generate_code

    ast = parse_spl(spl_src)
    if ast is None:
        raise ValueError("Parse failed; cannot generate BASIC.")
    inter = generate_code(ast)
    return intermediate_to_basic(inter, start=start, step=step)

# --- CLI: python basicify.py input.spl [output.bas] ---
if __name__ == "__main__":
    import sys, pathlib
    if len(sys.argv) < 2:
        print("Usage: python basicify.py <input.spl> [output.bas]")
        sys.exit(1)

    inp = pathlib.Path(sys.argv[1])
    out = pathlib.Path(sys.argv[2]) if len(sys.argv) >= 3 else inp.with_suffix(".bas")

    src = inp.read_text(encoding="utf-8")
    basic = compile_spl_to_basic(src)  # default numbering 10,20,30,...

    out.write_text(basic + "\n", encoding="utf-8")
    print(f"Wrote {out}:\n")
    print(basic)
