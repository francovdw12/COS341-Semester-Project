from typing import Any, List, Tuple, Optional

# ----------------- tiny helpers to read the AST -----------------

def _lin(node: Any) -> Optional[int]:
    if isinstance(node, tuple):
        tag = node[0]
        if tag in ('VAR', 'NAME', 'ATOM_NUM'):
            return node[2]
        if tag == 'ATOM_VAR':
            return _lin(node[1])
    return None

def _varname(var_node: Tuple[str, str, int]) -> str:
    return var_node[1]  # ('VAR', name, line)

def _nametext(name_node: Tuple[str, str, int]) -> str:
    return name_node[1]  # ('NAME', name, line)

def _atom_to_str(atom: Tuple) -> str:
    if atom[0] == 'ATOM_VAR':
        return _varname(atom[1])
    if atom[0] == 'ATOM_NUM':
        return str(atom[1])
    raise ValueError(f"Unexpected ATOM node: {atom[0]}")

# ----------------- code generator -----------------

class CodeGen:
    def __init__(self):
        self.lines: List[str] = []
        self._lab = 0

    def emit(self, s: str) -> None:
        self.lines.append(s)

    def label(self, name: str) -> None:
        # Our target uses REM instead of LABEL
        self.emit(f"REM {name}")

    def new_label(self, prefix: str = "L") -> str:
        self._lab += 1
        return f"{prefix}{self._lab:04d}"

    # ---- numeric expressions (used only where a numeric value is required) ----

    def term_to_expr(self, term: Tuple) -> str:
        tag = term[0]
        if tag == 'TERM_ATOM':
            return _atom_to_str(term[1])

        if tag == 'TERM_UNOP':
            op, sub = term[1], term[2]
            if op == 'NEG':
                return f"-({self.term_to_expr(sub)})"
            # 'NOT' should never appear in numeric contexts if type-checking ran
            raise ValueError("Boolean 'not' used where a numeric expression is required")

        if tag == 'TERM_BINOP':
            left, op, right = term[1], term[2], term[3]
            # arithmetic ops only
            opmap = {'PLUS': '+', 'MINUS': '-', 'MULT': '*', 'DIV': '/'}
            if op in opmap:
                return f"({self.term_to_expr(left)} {opmap[op]} {self.term_to_expr(right)})"
            # boolean/comparison must not appear here after type-check
            raise ValueError("Non-numeric operator used where a numeric expression is required")

        raise ValueError(f"Unknown TERM node: {tag}")

    # ---- conditions (emit jumps only; false = fall-through) ----
    # We generate only IF ... THEN <true_label> (no ELSE in the target),
    # and we compose AND/OR/NOT via cascading (Fig 6.8-style).

    def cond_goto_true(self, term: Tuple, true_label: str) -> None:
        tag = term[0]
        if tag == 'TERM_ATOM':
            # an ATOM as TERM is numeric; only nonzero truth is not modeled in SPL typing.
            # With the worksheet typing, TERM is boolean here only if produced by ops.
            # We'll be conservative: treat non-zero constants as true, but in practice
            # such cases won't appear if your type-checker is active.
            atom = term[1]
            if atom[0] == 'ATOM_NUM':
                if atom[1] != 0:
                    self.emit(f"GOTO {true_label}")
                # else: fall-through
                return
            # ATOM_VAR cannot be boolean by spec; ignore.
            return

        if tag == 'TERM_UNOP':
            op, sub = term[1], term[2]
            if op == 'NOT':
                self.cond_goto_false(sub, true_label)
                return
            if op == 'NEG':
                # numeric negation in a boolean context shouldn't occur after typing
                return

        if tag == 'TERM_BINOP':
            left, op, right = term[1], term[2], term[3]

            # comparisons: emit single IF
            if op in ('EQ', 'GT'):
                cmpmap = {'EQ': '=', 'GT': '>'}
                l = self.term_to_expr(left)
                r = self.term_to_expr(right)
                self.emit(f"IF {l} {cmpmap[op]} {r} THEN {true_label}")
                return

            # boolean AND / OR via cascading
            if op == 'AND':
                mid = self.new_label("T")
                self.cond_goto_true(left, mid)     # if left true, check right
                # else fall through (false)
                self.label(mid)
                self.cond_goto_true(right, true_label)
                return

            if op == 'OR':
                self.cond_goto_true(left, true_label)
                self.cond_goto_true(right, true_label)
                return

            # arithmetic in a boolean context shouldn't happen after typing
            return

        # Unknown node → do nothing (fall-through == false)
        return

    def cond_goto_false(self, term: Tuple, false_label: str) -> None:
        # Emit a jump to false_label when condition is false.
        # Implemented via small patterns that keep to IF/GOTO/REM only.
        tag = term[0]
        if tag == 'TERM_UNOP' and term[1] == 'NOT':
            # not X is false when X is true
            self.cond_goto_true(term[2], false_label)
            return

        if tag == 'TERM_BINOP':
            left, op, right = term[1], term[2], term[3]

            if op in ('EQ', 'GT'):
                # IF cond THEN Lskip ; GOTO false ; REM Lskip
                lskip = self.new_label("S")
                cmpmap = {'EQ': '=', 'GT': '>'}
                l = self.term_to_expr(left)
                r = self.term_to_expr(right)
                self.emit(f"IF {l} {cmpmap[op]} {r} THEN {lskip}")
                self.emit(f"GOTO {false_label}")
                self.label(lskip)
                return

            if op == 'AND':
                # false if left false OR right false
                self.cond_goto_false(left, false_label)
                self.cond_goto_false(right, false_label)
                return

            if op == 'OR':
                # false only if BOTH are false
                ldone = self.new_label("D")
                self.cond_goto_true(left, ldone)      # if left true, skip jumping
                self.cond_goto_false(right, false_label)
                self.label(ldone)
                return

        # For other forms, we don't emit a jump; fall-through means "not false".
        return

    # ---- statements / algorithms ----

    def gen_instr(self, instr: Tuple) -> None:
        tag = instr[0]

        if tag == 'INSTR_HALT':
            self.emit("STOP")
            return

        if tag == 'INSTR_PRINT':
            out = instr[1]
            if out[0] == 'OUTPUT_STRING':
                s = out[1]
                self.emit(f'PRINT "{s}"')
            elif out[0] == 'OUTPUT_ATOM':
                self.emit(f"PRINT {_atom_to_str(out[1])}")
            else:
                raise ValueError("Unknown OUTPUT node")
            return

        if tag == 'INSTR_CALL':
            name_node, in_list = instr[1], instr[2]
            callee = _nametext(name_node)
            args = " ".join(_atom_to_str(a) for a in in_list)
            self.emit(f"CALL {callee} ( {args} )")
            return

        if tag == 'ASSIGN_CALL':
            var_node, name_node, in_list = instr[1], instr[2], instr[3]
            lhs = _varname(var_node)
            callee = _nametext(name_node)
            args = " ".join(_atom_to_str(a) for a in in_list)
            self.emit(f"{lhs} = CALL {callee} ( {args} )")
            return

        if tag == 'ASSIGN_TERM':
            var_node, term = instr[1], instr[2]
            lhs = _varname(var_node)
            rhs = self.term_to_expr(term)
            self.emit(f"{lhs} = {rhs}")
            return

        if tag == 'BRANCH_IF':
            cond, then_algo = instr[1], instr[2]
            L_then = self.new_label("T")
            L_exit = self.new_label("X")

            # IF cond THEN L_then
            self.cond_goto_true(cond, L_then)
            # False path: skip then-part
            self.emit(f"GOTO {L_exit}")
            # Then-part
            self.label(L_then)
            self.gen_algo(then_algo)
            self.label(L_exit)
            return

        if tag == 'BRANCH_IF_ELSE':
            cond, then_algo, else_algo = instr[1], instr[2], instr[3]
            L_then = self.new_label("T")
            L_exit = self.new_label("X")

            # IF cond THEN L_then
            self.cond_goto_true(cond, L_then)
            # else-part first (per spec style)
            self.gen_algo(else_algo)
            self.emit(f"GOTO {L_exit}")
            # then-part
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
            # exit when cond is true
            self.cond_goto_true(cond, L_exit)
            self.emit(f"GOTO {L_start}")
            self.label(L_exit)
            return

        raise ValueError(f"Unknown INSTR node: {tag}")

    def gen_algo(self, algo_list: List[Tuple]) -> None:
        for instr in algo_list:
            self.gen_instr(instr)

    # ----------------- entry point -----------------

    def gen(self, ast: Tuple) -> str:
        if not (isinstance(ast, tuple) and ast and ast[0] == 'SPL_PROG'):
            raise ValueError("Top-level AST must be SPL_PROG")
        _, globals_vars, procdefs, funcdefs, mainprog = ast

        # Decls and def-bodies do not emit code now (saved for inlining later)
        # Generate only MAIN algorithm:
        main_algo = mainprog[2]
        self.gen_algo(main_algo)
        return "\n".join(self.lines)

# ----------------- public helpers -----------------

def generate_code(ast: Tuple) -> str:
    """Return intermediate code (string) for the given SPL AST."""
    return CodeGen().gen(ast)

def write_code_to_file(ast: Tuple, path: str) -> None:
    code = generate_code(ast)
    with open(path, "w", encoding="utf-8") as f:
        f.write(code + "\n")