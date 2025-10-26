# Performs type checking for our compiler

from typing import Any, Dict, List, Optional, Set, Tuple

NUM, BOOL = 'numeric', 'boolean'

#  small AST helpers 
def _lin(node: Any) -> Optional[int]:
    """Best-effort line extraction for helpful messages."""
    if isinstance(node, tuple):
        tag = node[0]
        if tag in ('VAR', 'NAME'):
            return node[2]
        if tag == 'ATOM_NUM':
            return node[2]
        if tag == 'ATOM_VAR':
            return _lin(node[1])
    return None

def _varname(var_node: Tuple[str, str, int]) -> str:
    # ('VAR', name, line)
    return var_node[1]

def _nametext(name_node: Tuple[str, str, int]) -> str:
    # ('NAME', name, line)
    return name_node[1]

def _varlist_names(var_list: List[Tuple[str, str, int]]) -> List[str]:
    return [_varname(v) for v in var_list]

# Type Analyser
class TypeAnalyserSpec:
    """Implements the worksheet's type attributions over the SPL AST."""
    def __init__(self, ast: Tuple):
        self.ast = ast
        self.errors: List[str] = []

        # For NAME typeless checks:
        self.vars_all: Set[str] = set() # every declared variable name (any scope)
        self.procs: Dict[str, Dict] = {} # name -> {'params': [...], 'locals': [...], 'algo': [...]}
        self.funcs: Dict[str, Dict] = {} # name -> {'params': [...], 'locals': [...], 'algo': [...], 'ret': atom}
        self.globals: Set[str] = set()
        self.main_vars: Set[str] = set()

        self.node_type: Dict[int, str] = {} # id(node) -> 'numeric' | 'boolean'

        self._collect_symbols()

    # symbol collection (for NAME typeless + arity hints)
    def _collect_symbols(self) -> None:
        if not (isinstance(self.ast, tuple) and self.ast and self.ast[0] == 'SPL_PROG'):
            self.errors.append("Internal: AST top-level is not SPL_PROG")
            return
        _, globals_vars, procdefs, funcdefs, mainprog = self.ast

        # globals
        self.globals = set(_varlist_names(globals_vars))
        self.vars_all |= self.globals

        # procedures
        for pdef in procdefs:
            # ('PDEF', ('NAME', pname, pline), ('PARAM', [vars...]), ('BODY', locals, algo))
            pname = _nametext(pdef[1])
            params = _varlist_names(pdef[2][1])
            locals_ = _varlist_names(pdef[3][1])
            algo = pdef[3][2]
            self.procs[pname] = {'params': params, 'locals': locals_, 'algo': algo}
            self.vars_all |= set(params)
            self.vars_all |= set(locals_)

        # functions
        for fdef in funcdefs:
            # ('FDEF', ('NAME', fname, fline), ('PARAM', [vars...]), ('BODY', locals, algo), ret_atom)
            fname = _nametext(fdef[1])
            params = _varlist_names(fdef[2][1])
            locals_ = _varlist_names(fdef[3][1])
            algo = fdef[3][2]
            ret_atom = fdef[4]
            self.funcs[fname] = {'params': params, 'locals': locals_, 'algo': algo, 'ret': ret_atom}
            self.vars_all |= set(params)
            self.vars_all |= set(locals_)

        # main
        self.main_vars = set(_varlist_names(mainprog[1]))
        self.vars_all |= self.main_vars

    # annotation helper
    def _note(self, node: Any, ty: str) -> None:
        if isinstance(node, tuple):
            self.node_type[id(node)] = ty

    # typing primitives
    def _type_atom(self, atom: Tuple) -> str:
        # ATOM ::= VAR | number
        if atom[0] == 'ATOM_VAR':
            self._note(atom, NUM)
            return NUM
        if atom[0] == 'ATOM_NUM':
            self._note(atom, NUM)
            return NUM
        self.errors.append(f"Type error: unknown ATOM form at line { _lin(atom) }")
        # default to numeric to avoid error cascades
        self._note(atom, NUM)
        return NUM

    def _type_term(self, term: Tuple) -> Optional[str]:
        tag = term[0]
        if tag == 'TERM_ATOM':
            t = self._type_atom(term[1])
            self._note(term, t)
            return t

        if tag == 'TERM_UNOP':
            op, sub = term[1], term[2]
            tsub = self._type_term(sub)
            if op == 'NEG':
                if tsub != NUM:
                    self.errors.append(f"Type error: 'neg' expects numeric at line { _lin(sub) }")
                self._note(term, NUM)
                return NUM
            if op == 'NOT':
                if tsub != BOOL:
                    self.errors.append(f"Type error: 'not' expects boolean at line { _lin(sub) }")
                self._note(term, BOOL)
                return BOOL
            self.errors.append(f"Type error: unknown UNOP '{op}'")
            return None

        if tag == 'TERM_BINOP':
            left, op, right = term[1], term[2], term[3]
            tl = self._type_term(left)
            tr = self._type_term(right)

            numeric_ops    = {'PLUS','MINUS','MULT','DIV'}
            boolean_ops    = {'AND','OR'}
            comparison_ops = {'EQ','GT'}

            if op in numeric_ops:
                if tl != NUM or tr != NUM:
                    self.errors.append(f"Type error: numeric op requires numeric terms at line { _lin(term) }")
                self._note(term, NUM)
                return NUM
            if op in boolean_ops:
                if tl != BOOL or tr != BOOL:
                    self.errors.append(f"Type error: boolean op requires boolean terms at line { _lin(term) }")
                self._note(term, BOOL)
                return BOOL
            if op in comparison_ops:
                if tl != NUM or tr != NUM:
                    self.errors.append(f"Type error: comparison requires numeric terms at line { _lin(term) }")
                self._note(term, BOOL)
                return BOOL

            self.errors.append(f"Type error: unknown BINOP '{op}'")
            return None

        self.errors.append(f"Type error: unknown TERM node '{tag}'")
        return None

    def _check_output(self, output: Tuple) -> None:
        # OUTPUT ::= ATOM (must be numeric) | string (fact)
        if output[0] == 'OUTPUT_ATOM':
            if self._type_atom(output[1]) != NUM:
                self.errors.append(f"Type error: print expects numeric atom at line { _lin(output) }")
            return
        if output[0] == 'OUTPUT_STRING':
            return  # fact
        self.errors.append("Type error: invalid OUTPUT")

    def _check_input(self, atoms: List[Tuple]) -> None:
        for a in atoms:
            if self._type_atom(a) != NUM:
                self.errors.append(f"Type error: input atom must be numeric at line { _lin(a) }")

    # instructions & algorithms
    def _check_instr(self, instr: Tuple) -> None:
        tag = instr[0]

        if tag == 'INSTR_HALT':
            return

        if tag == 'INSTR_PRINT':
            self._check_output(instr[1])
            return

        if tag == 'INSTR_CALL':
            # NAME ( INPUT )
            name_node, args = instr[1], instr[2]
            callee = _nametext(name_node)
            if callee in self.vars_all:
                self.errors.append(
                    f"Type error: procedure name '{callee}' is not typeless (clashes with a variable) at line { _lin(name_node) }"
                )
            if callee not in self.procs:
                self.errors.append(
                    f"Type error: '{callee}' is not a procedure at line { _lin(name_node) }"
                )
            self._check_input(args)
            # (Optional) arity consistency
            if callee in self.procs:
                want, got = len(self.procs[callee]['params']), len(args)
                if want != got:
                    self.errors.append(
                        f"Type error: procedure '{callee}' expects {want} args, got {got} at line { _lin(name_node) }"
                    )
            return

        if tag == 'ASSIGN_CALL':
            # VAR = NAME ( INPUT ) NAME typeless and a function; VAR numeric (fact)
            var_node, name_node, args = instr[1], instr[2], instr[3]
            fname = _nametext(name_node)
            if fname in self.vars_all:
                self.errors.append(
                    f"Type error: function name '{fname}' is not typeless (clashes with a variable) at line { _lin(name_node) }"
                )
            if fname not in self.funcs:
                self.errors.append(
                    f"Type error: '{fname}' is not a function at line { _lin(name_node) }"
                )
            self._check_input(args)
            if fname in self.funcs:
                want, got = len(self.funcs[fname]['params']), len(args)
                if want != got:
                    self.errors.append(
                        f"Type error: function '{fname}' expects {want} args, got {got} at line { _lin(name_node) }"
                    )
            return

        if tag == 'ASSIGN_TERM':
            # VAR = TERM - both numeric
            _lhs, term = instr[1], instr[2]
            t = self._type_term(term)
            if t != NUM:
                self.errors.append(f"Type error: assignment RHS must be numeric at line { _lin(term) }")
            return

        if tag == 'LOOP_WHILE':
            term, algo = instr[1], instr[2]
            if self._type_term(term) != BOOL:
                self.errors.append(f"Type error: while-condition must be boolean at line { _lin(term) }")
            self._check_algo(algo)
            return

        if tag == 'LOOP_DO_UNTIL':
            algo, term = instr[1], instr[2]
            self._check_algo(algo)
            if self._type_term(term) != BOOL:
                self.errors.append(f"Type error: until-condition must be boolean at line { _lin(term) }")
            return

        if tag == 'BRANCH_IF':
            term, algo = instr[1], instr[2]
            if self._type_term(term) != BOOL:
                self.errors.append(f"Type error: if-condition must be boolean at line { _lin(term) }")
            self._check_algo(algo)
            return

        if tag == 'BRANCH_IF_ELSE':
            term, then_algo, else_algo = instr[1], instr[2], instr[3]
            if self._type_term(term) != BOOL:
                self.errors.append(f"Type error: if-condition must be boolean at line { _lin(term) }")
            self._check_algo(then_algo)
            self._check_algo(else_algo)
            return

        self.errors.append(f"Type error: unknown INSTR '{tag}'")

    def _check_algo(self, algo: List[Tuple]) -> None:
        for instr in algo:
            self._check_instr(instr)

    # node-level wrappers
    def _check_param(self, param_node: Tuple) -> None:
        # PARAM ::= MAXTHREE - vars are numeric (fact) so nothing extra to enforce here
        return

    def _check_body(self, body_node: Tuple) -> None:
        # BODY ::= local { MAXTHREE } ALGO
        locals_list, algo = body_node[1], body_node[2]
        # MAXTHREE elements are VAR (numeric, fact)
        self._check_algo(algo)

    # driver
    def run(self) -> bool:
        if not (isinstance(self.ast, tuple) and self.ast and self.ast[0] == 'SPL_PROG'):
            self.errors.append("Type error: invalid AST")
            return False

        _, _globals_vars, procdefs, funcdefs, mainprog = self.ast

        # PROCDEFS
        for pdef in procdefs:
            pname_node = pdef[1]
            pname = _nametext(pname_node)
            if pname in self.vars_all:
                self.errors.append(
                    f"Type error: procedure name '{pname}' is not typeless (clashes with a variable) at line { _lin(pname_node) }"
                )
            self._check_param(pdef[2])
            self._check_body(pdef[3])

        # FUNCDEFS
        for fdef in funcdefs:
            fname_node = fdef[1]
            fname = _nametext(fname_node)
            if fname in self.vars_all:
                self.errors.append(
                    f"Type error: function name '{fname}' is not typeless (clashes with a variable) at line { _lin(fname_node) }"
                )
            self._check_param(fdef[2])
            self._check_body(fdef[3])
            # 'return ATOM' must be numeric
            ret_atom = fdef[4]
            if self._type_atom(ret_atom) != NUM:
                self.errors.append(
                    f"Type error: function return must be numeric at line { _lin(ret_atom) }"
                )

        # MAINPROG
        main_algo = mainprog[2]
        self._check_algo(main_algo)

        return not self.errors

# PUBLIC FUNCS
def analyze_types_spec(ast: Tuple, want_annotations: bool = False):
    ta = TypeAnalyserSpec(ast)
    ta.run()
    if want_annotations:
        return ta.errors, ta.node_type
    return ta.errors

def print_types(ast: Any, node_types: Dict[int, str], indent: int = 0) -> None:
    if isinstance(ast, tuple):
        tag = ast[0]
        ty = node_types.get(id(ast))
        line = _lin(ast)
        line_s = f" [line {line}]" if line is not None else ""
        ty_s = f" :: {ty}" if ty else ""
        extra = ""
        if tag == 'ATOM_NUM':
            extra = f" {ast[1]}"
        if tag == 'ATOM_VAR':
            extra = f" {_varname(ast[1])}"
        print("  " * indent + f"{tag}{extra}{line_s}{ty_s}")
        for ch in ast[1:]:
            print_types(ch, node_types, indent + 1)
    elif isinstance(ast, list):
        print("  " * indent + "[")
        for it in ast:
            print_types(it, node_types, indent + 1)
        print("  " * indent + "]")
    else:
        print("  " * indent + repr(ast))