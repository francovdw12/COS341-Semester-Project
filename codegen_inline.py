# codegen_inline.py
# SPL → Intermediate (inlined, no CALL) so it runs after BASIC numbering.

from typing import Any, Dict, List, Tuple

# ------- small AST helpers -------
def _varname(var_node: Tuple[str, str, int]) -> str:  # ('VAR', name, line)
    return var_node[1]

def _nametext(name_node: Tuple[str, str, int]) -> str:  # ('NAME', name, line)
    return name_node[1]

# ------- inlining codegen -------
class InlineCodeGen:
    def __init__(self, ast: Tuple):
        self.ast = ast
        self.lines: List[str] = []
        self._lab = 0
        self._v = 0
        self.scope_stack: List[Dict[str, str]] = []  # var -> renamed

        self.procs: Dict[str, Dict] = {}
        self.funcs: Dict[str, Dict] = {}
        self._collect_defs()

    # collect procedure/function definitions
    def _collect_defs(self):
        if not (isinstance(self.ast, tuple) and self.ast and self.ast[0] == 'SPL_PROG'):
            raise ValueError("Top-level AST must be SPL_PROG")
        _, _globals_vars, procdefs, funcdefs, _mainprog = self.ast

        for pdef in procdefs:
            # ('PDEF', name, param, body)
            pname = _nametext(pdef[1])
            params = [_varname(v) for v in pdef[2][1]]          # ('PARAM', [VAR...])
            locals_ = [_varname(v) for v in pdef[3][1]]         # ('BODY', locals, algo)
            algo = pdef[3][2]
            self.procs[pname] = dict(params=params, locals=locals_, algo=algo)

        for fdef in funcdefs:
            # ('FDEF', name, param, ('BODY', locals, algo), atom)
            fname = _nametext(fdef[1])
            params = [_varname(v) for v in fdef[2][1]]
            locals_ = [_varname(v) for v in fdef[3][1]]
            algo = fdef[3][2]
            ret = fdef[4]
            self.funcs[fname] = dict(params=params, locals=locals_, algo=algo, ret=ret)

    # low-level emit/labels/vars
    def emit(self, s: str) -> None:
        self.lines.append(s)

    def label(self, name: str) -> None:
        self.emit(f"REM {name}")

    def new_label(self, prefix: str) -> str:
        self._lab += 1
        return f"{prefix}{self._lab:04d}"

    def fresh_var(self, base: str, kind: str) -> str:
        self._v += 1
        return f"{kind}{self._v}{base}"  # BASIC-friendly

    # name mapping (params/locals → fresh)
    def map_name(self, name: str) -> str:
        for mp in reversed(self.scope_stack):
            if name in mp:
                return mp[name]
        return name  # global/main

    # atom/term to string (with mapping)
    def atom_to_str(self, atom: Tuple) -> str:
        if atom[0] == 'ATOM_NUM':
            return str(atom[1])
        if atom[0] == 'ATOM_VAR':
            return self.map_name(_varname(atom[1]))
        raise ValueError(f"Bad ATOM: {atom[0]}")

    def term_to_expr(self, term: Tuple) -> str:
        tag = term[0]
        if tag == 'TERM_ATOM':
            return self.atom_to_str(term[1])
        if tag == 'TERM_UNOP':
            op, sub = term[1], term[2]
            if op == 'NEG':
                return f"-({self.term_to_expr(sub)})"
            if op == 'NOT':
                raise ValueError("Boolean NOT used where numeric expected")
        if tag == 'TERM_BINOP':
            l, op, r = term[1], term[2], term[3]
            m = {'PLUS': '+', 'MINUS': '-', 'MULT': '*', 'DIV': '/'}
            if op in m:
                return f"({self.term_to_expr(l)} {m[op]} {self.term_to_expr(r)})"
            raise ValueError("Non-numeric BINOP used in numeric context")
        raise ValueError(f"Unknown TERM: {tag}")

    # conditions: emit jump-to-true only; cascade for AND/OR/NOT
    def cond_goto_true(self, term: Tuple, true_lab: str) -> None:
        if term[0] == 'TERM_UNOP' and term[1] == 'NOT':
            self.cond_goto_false(term[2], true_lab)
            return
        if term[0] == 'TERM_BINOP':
            l, op, r = term[1], term[2], term[3]
            if op in ('EQ', 'GT'):
                cmpmap = {'EQ': '=', 'GT': '>'}
                self.emit(f"IF {self.term_to_expr(l)} {cmpmap[op]} {self.term_to_expr(r)} THEN {true_lab}")
                return
            if op == 'AND':
                mid = self.new_label("T")
                self.cond_goto_true(l, mid)
                self.label(mid)
                self.cond_goto_true(r, true_lab)
                return
            if op == 'OR':
                self.cond_goto_true(l, true_lab)
                self.cond_goto_true(r, true_lab)
                return
        # anything else: treated as false (well-typed SPL won’t put numerics here)

    def cond_goto_false(self, term: Tuple, false_lab: str) -> None:
        if term[0] == 'TERM_UNOP' and term[1] == 'NOT':
            self.cond_goto_true(term[2], false_lab)
            return
        if term[0] == 'TERM_BINOP':
            l, op, r = term[1], term[2], term[3]
            if op in ('EQ', 'GT'):
                skip = self.new_label("S")
                cmpmap = {'EQ': '=', 'GT': '>'}
                self.emit(f"IF {self.term_to_expr(l)} {cmpmap[op]} {self.term_to_expr(r)} THEN {skip}")
                self.emit(f"GOTO {false_lab}")
                self.label(skip)
                return
            if op == 'AND':
                self.cond_goto_false(l, false_lab)
                self.cond_goto_false(r, false_lab)
                return
            if op == 'OR':
                done = self.new_label("D")
                self.cond_goto_true(l, done)
                self.cond_goto_false(r, false_lab)
                self.label(done)
                return

    # statements (with inlining)
    def gen_instr(self, instr: Tuple) -> None:
        tag = instr[0]

        if tag == 'INSTR_HALT':
            self.emit("STOP"); return

        if tag == 'INSTR_PRINT':
            out = instr[1]
            if out[0] == 'OUTPUT_STRING':
                self.emit(f'PRINT "{out[1]}"')
            else:
                self.emit(f"PRINT {self.atom_to_str(out[1])}")
            return

        if tag == 'ASSIGN_TERM':
            lhs = self.map_name(_varname(instr[1]))
            rhs = self.term_to_expr(instr[2])
            self.emit(f"{lhs} = {rhs}")
            return

        if tag == 'BRANCH_IF':
            cond, then_algo = instr[1], instr[2]
            L_then = self.new_label("T")
            L_exit = self.new_label("X")
            self.cond_goto_true(cond, L_then)
            self.emit(f"GOTO {L_exit}")
            self.label(L_then)
            self.gen_algo(then_algo)
            self.label(L_exit)
            return

        if tag == 'BRANCH_IF_ELSE':
            cond, then_algo, else_algo = instr[1], instr[2], instr[3]
            L_then = self.new_label("T")
            L_exit = self.new_label("X")
            self.cond_goto_true(cond, L_then)
            self.gen_algo(else_algo)
            self.emit(f"GOTO {L_exit}")
            self.label(L_then)
            self.gen_algo(then_algo)
            self.label(L_exit)
            return

        if tag == 'LOOP_WHILE':
            cond, body = instr[1], instr[2]
            L_start = self.new_label("W")
            L_body  = self.new_label("WB")
            L_exit  = self.new_label("WX")
            self.label(L_start)
            self.cond_goto_true(cond, L_body)
            self.emit(f"GOTO {L_exit}")
            self.label(L_body)
            self.gen_algo(body)
            self.emit(f"GOTO {L_start}")
            self.label(L_exit)
            return

        if tag == 'LOOP_DO_UNTIL':
            body, cond = instr[1], instr[2]
            L_start = self.new_label("D")
            L_exit  = self.new_label("DX")
            self.label(L_start)
            self.gen_algo(body)
            self.cond_goto_true(cond, L_exit)
            self.emit(f"GOTO {L_start}")
            self.label(L_exit)
            return

        # ---- inline calls ----
        if tag == 'INSTR_CALL':
            name_node, actuals = instr[1], instr[2]
            self._inline_proc(_nametext(name_node), actuals)
            return

        if tag == 'ASSIGN_CALL':
            lhs_node, name_node, actuals = instr[1], instr[2], instr[3]
            self._inline_func(self.map_name(_varname(lhs_node)), _nametext(name_node), actuals)
            return

        raise ValueError(f"Unknown INSTR {tag}")

    def gen_algo(self, algo_list: List[Tuple]) -> None:
        for instr in algo_list:
            self.gen_instr(instr)

    # inlining helpers
    def _inline_proc(self, pname: str, actuals: List[Tuple]) -> None:
        info = self.procs.get(pname)
        if not info:
            self.emit(f"REM UNKNOWN_PROC {pname}")
            return
        params, locals_, body = info['params'], info['locals'], info['algo']

        mp: Dict[str, str] = {}
        for p in params:  mp[p] = self.fresh_var(p, 'P')
        for l in locals_: mp[l] = self.fresh_var(l, 'L')
        self.scope_stack.append(mp)

        for p, a in zip(params, actuals):
            self.emit(f"{mp[p]} = {self.atom_to_str(a)}")

        self.gen_algo(body)
        self.scope_stack.pop()

    def _inline_func(self, lhs: str, fname: str, actuals: List[Tuple]) -> None:
        info = self.funcs.get(fname)
        if not info:
            self.emit(f"REM UNKNOWN_FUNC {fname}")
            return
        params, locals_, body, ret = info['params'], info['locals'], info['algo'], info['ret']

        mp: Dict[str, str] = {}
        for p in params:  mp[p] = self.fresh_var(p, 'P')
        for l in locals_: mp[l] = self.fresh_var(l, 'L')
        self.scope_stack.append(mp)

        for p, a in zip(params, actuals):
            self.emit(f"{mp[p]} = {self.atom_to_str(a)}")

        self.gen_algo(body)
        self.emit(f"{lhs} = {self.atom_to_str(ret)}")
        self.scope_stack.pop()

    # entry point
    def gen(self) -> str:
        _, _g, _p, _f, mainprog = self.ast
        main_algo = mainprog[2]
        self.gen_algo(main_algo)
        return "\n".join(self.lines)

def generate_code(ast: Tuple) -> str:
    return InlineCodeGen(ast).gen()

# convenience: CLI to dump inlined intermediate
if __name__ == "__main__":
    import sys, pathlib
    from parser import parse_spl
    if len(sys.argv) < 2:
        print("Usage: python codegen_inline.py <input.spl> [output.ic.txt]")
        sys.exit(1)
    inp = pathlib.Path(sys.argv[1])
    out = pathlib.Path(sys.argv[2]) if len(sys.argv) >= 3 else inp.with_suffix(".inlined.ic.txt")
    src = inp.read_text(encoding="utf-8")
    ast = parse_spl(src)
    if ast is None:
        print("Parse failed"); sys.exit(2)
    code = generate_code(ast)
    out.write_text(code + "\n", encoding="utf-8")
    print(f"Wrote {out}")
