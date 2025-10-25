# semantics.py
# Static semantics (scoping + basic type checks) for SPL
# Works with your existing lexer/parser that returns a nested tuple/list AST.

from collections import defaultdict
from typing import Any, Dict, List, Optional, Tuple, Set

Type = str  # 'int' | 'bool' | 'unknown'
INT, BOOL, UNKNOWN = 'int', 'bool', 'unknown'

# ---------- Utilities: node IDs over your tuple-based AST ----------

class NodeIDs:
    """Assigns a unique integer ID to every tuple node in the AST."""
    def __init__(self) -> None:
        self._next = 1
        self.id_of: Dict[int, int] = {}   # id(tuple_obj) -> node_id
        self.info: Dict[int, Dict[str, Any]] = {}  # node_id -> {'tag': str, 'scope': str}

    def assign(self, node: Any, scope: str = 'Everywhere') -> Optional[int]:
        if isinstance(node, tuple) and node:
            nid = self.id_of.get(id(node))
            if nid is None:
                nid = self._next
                self._next += 1
                self.id_of[id(node)] = nid
                tag = node[0]
                self.info[nid] = {'tag': tag, 'scope': scope}
                # Recurse into children
                for child in node[1:]:
                    self.assign(child, scope)
            return nid
        elif isinstance(node, list):
            for child in node:
                self.assign(child, scope)
        # primitives ignored
        return None

    def set_scope_recursive(self, node: Any, scope: str) -> None:
        """After initial assignment, overwrite scope for a subtree (PDEF/FDEF/Maine etc.)."""
        if isinstance(node, tuple) and node:
            nid = self.id_of.get(id(node))
            if nid is None:
                return
            self.info[nid]['scope'] = scope
            for child in node[1:]:
                self.set_scope_recursive(child, scope)
        elif isinstance(node, list):
            for child in node:
                self.set_scope_recursive(child, scope)


# ---------- Symbol structures ----------

class Symtab:
    """
    Program-wide symbol aggregates (indexed by names) plus per-declaration entries
    keyed by node-id (foreign key).
    """
    def __init__(self) -> None:
        # Declarations (name -> info)
        self.globals: Dict[str, Dict[str, Any]] = {}
        self.procs: Dict[str, Dict[str, Any]] = {}   # params, local vars, body, node_id
        self.funcs: Dict[str, Dict[str, Any]] = {}   # params, local vars, body, node_id
        self.main: Dict[str, Any] = {'vars': set(), 'algo': None}

        # All declared variable names across *all* scopes, to check "Everywhere" clashes
        self.all_var_names: Set[str] = set()

        # Per-variable declaration entry keyed by node-id
        # Example value: {'name': 'x', 'decl_kind': 'global'|'main'|'param'|'local',
        #                 'scope_label': 'Local(proc foo)' etc., 'type': 'unknown'}
        self.var_decls_by_node: Dict[int, Dict[str, Any]] = {}

        # Map VAR-usage node-id -> var-decl node-id (resolution)
        self.usage_to_decl: Dict[int, int] = {}

    def snapshot(self) -> str:
        lines = []
        lines.append("== Globals ==")
        lines.append(f"vars: {sorted(self.globals.keys())}")
        lines.append("== Procedures ==")
        for name, info in self.procs.items():
            lines.append(f"  proc {name}(params={info['params']}) locals={sorted(info['locals'])}")
        lines.append("== Functions ==")
        for name, info in self.funcs.items():
            lines.append(f"  func {name}(params={info['params']}) locals={sorted(info['locals'])}")
        lines.append("== Main ==")
        lines.append(f"  vars={sorted(self.main['vars'])}")
        lines.append("== Var Decls (by node-id) ==")
        for nid, d in sorted(self.var_decls_by_node.items()):
            lines.append(f"  {nid}: {d['name']}  kind={d['decl_kind']}  scope={d['scope_label']}  type={d['type']}")
        return "\n".join(lines)


# ---------- Error collector ----------

class Errors:
    def __init__(self) -> None:
        self.items: List[str] = []

    def add(self, msg: str) -> None:
        self.items.append(msg)

    def extend(self, msgs: List[str]) -> None:
        self.items.extend(msgs)

    def ok(self) -> bool:
        return not self.items

# ---------- Helpers over your AST shape ----------

def is_tag(node: Any, tag: str) -> bool:
    return isinstance(node, tuple) and node and node[0] == tag

def name_of_name_node(name_node: Tuple[str, str]) -> str:
    # ('NAME', 'foo')
    return name_node[1]

def name_of_var_node(var_node: Tuple[str, str]) -> str:
    # ('VAR', 'x')
    return var_node[1]

def names_from_varlist(varlist: List[Tuple[str, str]]) -> List[str]:
    return [name_of_var_node(v) for v in varlist]

def param_list_from_param_node(param_node: Tuple[str, List[Tuple[str, str]]]) -> List[Tuple[str, str]]:
    # ('PARAM', [ ('VAR','x'), ... ])
    return param_node[1]

def body_unpack(body_node: Tuple[str, List[Tuple[str, str]], List[Any]]) -> Tuple[List[Tuple[str, str]], List[Any]]:
    # ('BODY', locals_list, algo_list)
    return body_node[1], body_node[2]

# ---------- Program collection + scope layout ----------

def assign_scopes_and_ids(ast: Tuple, ids: NodeIDs) -> None:
    """Assign node IDs and scope labels per your SPL_PROG layout."""
    ids.assign(ast, scope='Everywhere')
    if not is_tag(ast, 'SPL_PROG'):
        return
    _, globals_vars, procdefs, funcdefs, mainprog = ast

    # Mark big regions
    ids.set_scope_recursive(globals_vars, 'Global')
    ids.set_scope_recursive(procdefs, 'Procedure')
    ids.set_scope_recursive(funcdefs, 'Function')
    ids.set_scope_recursive(mainprog, 'Main')

    # Within each PDEF/FDEF subtree, mark as Local(proc X)/Local(func F)
    # procdefs = [PDEF, ...]; pdef = ('PDEF', name_node, param_node, body_node)
    for pdef in procdefs:
        if is_tag(pdef, 'PDEF'):
            pname = name_of_name_node(pdef[1])
            ids.set_scope_recursive(pdef, f"Local(proc {pname})")
    for fdef in funcdefs:
        if is_tag(fdef, 'FDEF'):
            fname = name_of_name_node(fdef[1])
            ids.set_scope_recursive(fdef, f"Local(func {fname})")

# ---------- Uniqueness checks ----------

def check_unique(names: List[str], what: str, errs: Errors, where: str) -> None:
    seen = set()
    for n in names:
        if n in seen:
            errs.add(f"Name-rule violation: duplicate {what} '{n}' in {where}")
        seen.add(n)

# ---------- Build symbols (globals, procs, funcs, main) ----------

def build_symbols(ast: Tuple, ids: NodeIDs, sym: Symtab, errs: Errors) -> None:
    if not is_tag(ast, 'SPL_PROG'):
        errs.add("Top node is not SPL_PROG")
        return
    _, globals_vars, procdefs, funcdefs, mainprog = ast

    # Globals: variables list (['VAR', name]...)
    gnames = names_from_varlist(globals_vars)  # globals_vars is [] or [ ('VAR',x), ... ]
    check_unique(gnames, 'global variable', errs, 'Global scope')
    for v in globals_vars:
        nid = ids.id_of[id(v)]
        name = name_of_var_node(v)
        sym.globals[name] = {'node_id': nid}
        sym.all_var_names.add(name)
        sym.var_decls_by_node[nid] = {'name': name, 'decl_kind': 'global',
                                      'scope_label': 'Global', 'type': UNKNOWN}

    # Procedures
    pnames: List[str] = []
    for pdef in procdefs:
        # ('PDEF', name_node, ('PARAM', [vars]), ('BODY', locals, algo))
        pname = name_of_name_node(pdef[1])
        pnames.append(pname)
    check_unique(pnames, 'procedure', errs, 'Procedure scope')
    for pdef in procdefs:
        pname = name_of_name_node(pdef[1])
        nid = ids.id_of[id(pdef)]
        params = names_from_varlist(param_list_from_param_node(pdef[2]))
        locals_list, _algo = body_unpack(pdef[3])
        locals_names = names_from_varlist(locals_list)
        # MAXTHREE uniqueness (params and locals separately)
        check_unique(params, f"parameter in proc '{pname}'", errs, f"Local(proc {pname})")
        check_unique(locals_names, f"local var in proc '{pname}'", errs, f"Local(proc {pname})")
        # No shadowing: local vs params
        for n in locals_names:
            if n in params:
                errs.add(f"Name-rule violation: local '{n}' shadows parameter in proc '{pname}'")
        # Record
        sym.procs[pname] = {'node_id': nid, 'params': params, 'locals': set(locals_names), 'algo': _algo}
        for v in param_list_from_param_node(pdef[2]):
            vnid = ids.id_of[id(v)]
            n = name_of_var_node(v)
            sym.var_decls_by_node[vnid] = {'name': n, 'decl_kind': 'param',
                                           'scope_label': f"Local(proc {pname})", 'type': UNKNOWN}
            sym.all_var_names.add(n)
        for v in locals_list:
            vnid = ids.id_of[id(v)]
            n = name_of_var_node(v)
            sym.var_decls_by_node[vnid] = {'name': n, 'decl_kind': 'local',
                                           'scope_label': f"Local(proc {pname})", 'type': UNKNOWN}
            sym.all_var_names.add(n)

    # Functions
    fnames: List[str] = []
    for fdef in funcdefs:
        fname = name_of_name_node(fdef[1])
        fnames.append(fname)
    check_unique(fnames, 'function', errs, 'Function scope')
    for fdef in funcdefs:
        fname = name_of_name_node(fdef[1])
        nid = ids.id_of[id(fdef)]
        params = names_from_varlist(param_list_from_param_node(fdef[2]))
        body_locals, body_algo = body_unpack(fdef[3])
        ret_atom = fdef[4]
        locals_names = names_from_varlist(body_locals)
        # MAXTHREE uniqueness & shadow rules
        check_unique(params, f"parameter in func '{fname}'", errs, f"Local(func {fname})")
        check_unique(locals_names, f"local var in func '{fname}'", errs, f"Local(func {fname})")
        for n in locals_names:
            if n in params:
                errs.add(f"Name-rule violation: local '{n}' shadows parameter in func '{fname}'")
        sym.funcs[fname] = {'node_id': nid, 'params': params, 'locals': set(locals_names),
                            'algo': body_algo, 'ret': ret_atom}
        for v in param_list_from_param_node(fdef[2]):
            vnid = ids.id_of[id(v)]
            n = name_of_var_node(v)
            sym.var_decls_by_node[vnid] = {'name': n, 'decl_kind': 'param',
                                           'scope_label': f"Local(func {fname})", 'type': UNKNOWN}
            sym.all_var_names.add(n)
        for v in body_locals:
            vnid = ids.id_of[id(v)]
            n = name_of_var_node(v)
            sym.var_decls_by_node[vnid] = {'name': n, 'decl_kind': 'local',
                                           'scope_label': f"Local(func {fname})", 'type': UNKNOWN}
            sym.all_var_names.add(n)

    # Main
    # ('MAINPROG', main_vars_list, algo_list)
    main_vars, main_algo = mainprog[1], mainprog[2]
    mnames = names_from_varlist(main_vars)
    check_unique(mnames, 'main variable', errs, 'Main scope')
    sym.main['vars'] = set(mnames)
    sym.main['algo'] = main_algo
    for v in main_vars:
        vnid = ids.id_of[id(v)]
        n = name_of_var_node(v)
        sym.var_decls_by_node[vnid] = {'name': n, 'decl_kind': 'main',
                                       'scope_label': 'Main', 'type': UNKNOWN}
        sym.all_var_names.add(n)

    # SPL_PROG everywhere-rule: no variable name equals any function/procedure name
    fn_set, pn_set = set(fnames), set(pnames)
    for varname in sym.all_var_names:
        if varname in fn_set:
            errs.add(f"Everywhere-rule: variable name '{varname}' equals a function name")
        if varname in pn_set:
            errs.add(f"Everywhere-rule: variable name '{varname}' equals a procedure name")
    # Functions vs procedures must also be distinct
    for n in (fn_set & pn_set):
        errs.add(f"Everywhere-rule: function name '{n}' equals a procedure name")


# ---------- Type & name resolution ----------

class TypeChecker:
    def __init__(self, ids: NodeIDs, sym: Symtab, errs: Errors) -> None:
        self.ids, self.sym, self.errs = ids, sym, errs
        # types by decl node-id
        self.types: Dict[int, Type] = {}  # mirrors sym.var_decls_by_node[node_id]['type']

    # --- Resolution by scope rules ---
    def resolve_var(self, name: str, ctx: Dict[str, Any], usage_node: Tuple) -> Optional[int]:
        """
        Return decl node-id for a variable by SPL scope rules, else None (undeclared).
        ctx: {'kind': 'proc'|'func'|'main', 'name': <id name>, 'params': set(), 'locals': set()}
        """
        # Search order depends on scope
        if ctx['kind'] in ('proc', 'func'):
            if name in ctx['params']:
                return self.find_decl_node(name, ctx['scope_label'], decl_kind='param')
            if name in ctx['locals']:
                return self.find_decl_node(name, ctx['scope_label'], decl_kind='local')
            if name in self.sym.globals:
                # global decl node
                return self.sym.globals[name]['node_id']
        elif ctx['kind'] == 'main':
            if name in self.sym.main['vars']:
                return self.find_decl_node(name, 'Main', decl_kind='main')
            if name in self.sym.globals:
                return self.sym.globals[name]['node_id']

        # Not found
        nid_use = self.ids.id_of.get(id(usage_node), None)
        self.errs.add(f"Undeclared variable: '{name}' in {ctx['scope_label']}")
        return None

    def find_decl_node(self, name: str, scope_label: str, decl_kind: str) -> Optional[int]:
        for nid, d in self.sym.var_decls_by_node.items():
            if d['name'] == name and d['decl_kind'] == decl_kind and d['scope_label'] == scope_label:
                return nid
        return None  # should not happen if tables built right

    def set_type(self, decl_nid: int, ty: Type) -> None:
        if decl_nid is None:
            return
        prev = self.sym.var_decls_by_node[decl_nid]['type']
        new = self.unify(prev, ty)
        if new == 'error':
            name = self.sym.var_decls_by_node[decl_nid]['name']
            self.errs.add(f"Type mismatch for '{name}': cannot unify {prev} with {ty}")
            return
        self.sym.var_decls_by_node[decl_nid]['type'] = new

    # --- Unification ---
    @staticmethod
    def unify(a: Type, b: Type) -> Type:
        if a == b:
            return a
        if a == UNKNOWN:
            return b
        if b == UNKNOWN:
            return a
        return 'error'

    # --- Term/type evaluation ---
    def check_atom(self, atom: Tuple, ctx: Dict[str, Any]) -> Type:
        if is_tag(atom, 'ATOM_NUM'):
            return INT
        if is_tag(atom, 'ATOM_VAR'):
            var_node = atom[1]  # ('VAR', name)
            name = name_of_var_node(var_node)
            decl_nid = self.resolve_var(name, ctx, var_node)
            if decl_nid is not None:
                self.sym.usage_to_decl[self.ids.id_of[id(var_node)]] = decl_nid
                # Use current known type (may be unknown)
                return self.sym.var_decls_by_node[decl_nid]['type']
            return UNKNOWN
        return UNKNOWN

    def check_term(self, term: Tuple, ctx: Dict[str, Any]) -> Type:
        if is_tag(term, 'TERM_ATOM'):
            return self.check_atom(term[1], ctx)

        if is_tag(term, 'TERM_UNOP'):
            op, sub = term[1], term[2]
            t = self.check_term(sub, ctx)
            if op == 'NEG':
                if t not in (INT, UNKNOWN):
                    self.errs.add("Type error: 'neg' expects int")
                return INT
            if op == 'NOT':
                if t not in (BOOL, UNKNOWN):
                    self.errs.add("Type error: 'not' expects bool")
                return BOOL

        if is_tag(term, 'TERM_BINOP'):
            left, op, right = term[1], term[2], term[3]
            tl = self.check_term(left, ctx)
            tr = self.check_term(right, ctx)
            if op in ('PLUS', 'MINUS', 'MULT', 'DIV'):
                if tl not in (INT, UNKNOWN) or tr not in (INT, UNKNOWN):
                    self.errs.add(f"Type error: '{op.lower()}' expects int,int")
                return INT
            if op in ('EQ', 'GT'):
                if tl not in (INT, UNKNOWN) or tr not in (INT, UNKNOWN):
                    self.errs.add(f"Type error: '{op.lower()}' expects int,int")
                return BOOL
            if op in ('AND', 'OR'):
                if tl not in (BOOL, UNKNOWN) or tr not in (BOOL, UNKNOWN):
                    self.errs.add(f"Type error: '{op.lower()}' expects bool,bool")
                return BOOL

        return UNKNOWN

    # --- Algo/instruction checks + constraints ---
    def expect_bool(self, term: Tuple, ctx: Dict[str, Any]) -> None:
        t = self.check_term(term, ctx)
        if t not in (BOOL, UNKNOWN):
            self.errs.add("Type error: condition must be boolean")

    def check_instr(self, instr: Tuple, ctx: Dict[str, Any]) -> None:
        tag = instr[0]
        if tag == 'INSTR_HALT':
            return
        if tag == 'INSTR_PRINT':
            out = instr[1]
            if is_tag(out, 'OUTPUT_ATOM'):
                self.check_atom(out[1], ctx)
            elif is_tag(out, 'OUTPUT_STRING'):
                pass  # strings are fine
            return
        if tag == 'INSTR_CALL':
            # procedure call: ('INSTR_CALL', name_node, args_list)
            name = name_of_name_node(instr[1])
            args = instr[2]
            if name not in self.sym.procs:
                self.errs.add(f"Call error: '{name}' is not a procedure")
            else:
                want = len(self.sym.procs[name]['params'])
                got = len(args)
                if want != got:
                    self.errs.add(f"Arity error in proc '{name}': expected {want}, got {got}")
            # Check atoms in args (but no param typing in spec)
            for a in args:
                if is_tag(a, 'ATOM_VAR') or is_tag(a, 'ATOM_NUM'):
                    self.check_atom(a, ctx)
            return
        if tag in ('ASSIGN_CALL', 'ASSIGN_TERM'):
            # Resolve LHS var (must exist per scope)
            lhs_var = instr[1]  # ('VAR', name)
            lname = name_of_var_node(lhs_var)
            decl_nid = self.resolve_var(lname, ctx, lhs_var)
            if decl_nid is None:
                return
            if tag == 'ASSIGN_CALL':
                # function call: ('ASSIGN_CALL', var, name_node, args)
                fname = name_of_name_node(instr[2])
                args = instr[3]
                if fname not in self.sym.funcs:
                    self.errs.add(f"Call error: '{fname}' is not a function")
                else:
                    want = len(self.sym.funcs[fname]['params'])
                    got = len(args)
                    if want != got:
                        self.errs.add(f"Arity error in func '{fname}': expected {want}, got {got}")
                for a in args:
                    if is_tag(a, 'ATOM_VAR') or is_tag(a, 'ATOM_NUM'):
                        self.check_atom(a, ctx)
                # Return type unknown (no spec), so we can't constrain lhs beyond "some value"
                # If you want: self.set_type(decl_nid, UNKNOWN)
            else:
                # ('ASSIGN_TERM', var, term)
                t = self.check_term(instr[2], ctx)
                self.set_type(decl_nid, t)
            return
        if tag == 'LOOP_WHILE':
            term = instr[1]
            algo = instr[2]
            self.expect_bool(term, ctx)
            for ins in algo: self.check_instr(ins, ctx)
            return
        if tag == 'LOOP_DO_UNTIL':
            algo = instr[1]; term = instr[2]
            for ins in algo: self.check_instr(ins, ctx)
            self.expect_bool(term, ctx)
            return
        if tag == 'BRANCH_IF':
            term = instr[1]; then = instr[2]
            self.expect_bool(term, ctx)
            for ins in then: self.check_instr(ins, ctx)
            return
        if tag == 'BRANCH_IF_ELSE':
            term = instr[1]; then = instr[2]; els = instr[3]
            self.expect_bool(term, ctx)
            for ins in then: self.check_instr(ins, ctx)
            for ins in els: self.check_instr(ins, ctx)
            return

    def check_algo(self, algo: List[Tuple], ctx: Dict[str, Any]) -> None:
        for ins in algo:
            self.check_instr(ins, ctx)

    def run(self, ast: Tuple) -> None:
        # Procedures
        for name, info in self.sym.procs.items():
            ctx = {'kind': 'proc',
                   'name': name,
                   'params': set(info['params']),
                   'locals': set(info['locals']),
                   'scope_label': f"Local(proc {name})"}
            self.check_algo(info['algo'], ctx)
        # Functions
        for name, info in self.sym.funcs.items():
            ctx = {'kind': 'func',
                   'name': name,
                   'params': set(info['params']),
                   'locals': set(info['locals']),
                   'scope_label': f"Local(func {name})"}
            self.check_algo(info['algo'], ctx)
            # return expr must be consistent (we can infer but spec doesn't force type)
            # If you want to type the return into a synthetic variable, do it here.
        # Main
        ctx = {'kind': 'main', 'name': 'main', 'params': set(), 'locals': set(self.sym.main['vars']),
               'scope_label': 'Main'}
        self.check_algo(self.sym.main['algo'], ctx)


# ---------- Public entry point ----------

def analyze_semantics(parse_tree: Tuple) -> Tuple[Symtab, NodeIDs, Errors]:
    """
    Given the AST returned by your parser, build IDs & symbol table and run checks.
    Returns (symtab, node_ids, errors)
    """
    errs = Errors()
    ids = NodeIDs()
    sym = Symtab()

    # 1) Assign IDs and region scopes
    assign_scopes_and_ids(parse_tree, ids)

    # 2) Build symbols & enforce declaration/uniqueness rules
    build_symbols(parse_tree, ids, sym, errs)

    # 3) Resolve names + type checks over algorithms
    tc = TypeChecker(ids, sym, errs)
    tc.run(parse_tree)

    return sym, ids, errs


# ---------- Minimal CLI test (optional) ----------

if __name__ == "__main__":
    from parser import parse_spl, print_parse_tree  # your existing module names

    code = """
    glob { x y }
    proc {
      foo(a) { local { t } print a; t = ( (5 PLUS 3) ); }   // invalid term (needs parentheses with binops)
    }
    func {
      sum(a b) { local { r } r = ( (a plus b) ); return r }
    }
    main {
      var { counter }
      counter = 5;
      print counter;
      halt
    }
    """
    tree = parse_spl(code)
    if tree:
        sym, ids, errs = analyze_semantics(tree)
        print("---- SYMBOL TABLE ----")
        print(sym.snapshot())
        print("\n---- ERRORS ----")
        if errs.ok():
            print("No semantic errors.")
        else:
            for e in errs.items:
                print("*", e)
