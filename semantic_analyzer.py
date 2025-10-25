"""
SPL Semantic Analyzer Implementation
COS341 Semester Project 2025

This module implements the scope analysis phase of the SPL compiler.
It includes:
1. Symbol Table with node ID foreign keys
2. Tree-crawling scope analyzer
3. Name-rule-violation and undeclared-variable error reporting
"""

from typing import Dict, List, Optional, Set, Tuple, Any
from enum import Enum


class ScopeType(Enum):
    """Types of scopes in SPL"""
    EVERYWHERE = "Everywhere"
    GLOBAL = "Global"
    PROCEDURE = "Procedure"
    FUNCTION = "Function"
    MAIN = "Main"
    LOCAL = "Local"


class SymbolType(Enum):
    """Types of symbols in SPL"""
    VARIABLE = "Variable"
    PROCEDURE = "Procedure"
    FUNCTION = "Function"


class SymbolTableEntry:
    """Entry in the symbol table"""
    
    def __init__(self, name: str, symbol_type: SymbolType, scope_type: ScopeType, 
                 node_id: int, scope_id: str, declaration_node_id: int):
        self.name = name
        self.symbol_type = symbol_type
        self.scope_type = scope_type
        self.node_id = node_id  # Foreign key to syntax tree node
        self.scope_id = scope_id  # Identifier for the scope this symbol belongs to
        self.declaration_node_id = declaration_node_id  # Node ID where symbol is declared
        
    def __repr__(self):
        return f"SymbolTableEntry(name='{self.name}', type={self.symbol_type.value}, scope={self.scope_type.value}, node_id={self.node_id})"


class ScopeInfo:
    """Information about a scope"""
    
    def __init__(self, scope_id: str, scope_type: ScopeType, parent_scope_id: Optional[str] = None):
        self.scope_id = scope_id
        self.scope_type = scope_type
        self.parent_scope_id = parent_scope_id
        self.symbols: Dict[str, SymbolTableEntry] = {}
        
    def add_symbol(self, symbol: SymbolTableEntry):
        """Add a symbol to this scope"""
        self.symbols[symbol.name] = symbol
        
    def get_symbol(self, name: str) -> Optional[SymbolTableEntry]:
        """Get a symbol from this scope"""
        return self.symbols.get(name)
        
    def has_symbol(self, name: str) -> bool:
        """Check if a symbol exists in this scope"""
        return name in self.symbols


class SymbolTable:
    """Symbol table for SPL compiler"""
    
    def __init__(self):
        self.entries: Dict[int, SymbolTableEntry] = {}  # node_id -> SymbolTableEntry
        self.scopes: Dict[str, ScopeInfo] = {}  # scope_id -> ScopeInfo
        self.node_id_counter = 1  # Counter for unique node IDs
        self.scope_id_counter = 1  # Counter for unique scope IDs
        
    def get_next_node_id(self) -> int:
        """Get the next unique node ID"""
        node_id = self.node_id_counter
        self.node_id_counter += 1
        return node_id
        
    def get_next_scope_id(self) -> str:
        """Get the next unique scope ID"""
        scope_id = f"scope_{self.scope_id_counter}"
        self.scope_id_counter += 1
        return scope_id
        
    def add_entry(self, entry: SymbolTableEntry):
        """Add an entry to the symbol table"""
        self.entries[entry.node_id] = entry
        
    def get_entry(self, node_id: int) -> Optional[SymbolTableEntry]:
        """Get an entry by node ID"""
        return self.entries.get(node_id)
        
    def add_scope(self, scope: ScopeInfo):
        """Add a scope to the symbol table"""
        self.scopes[scope.scope_id] = scope
        
    def get_scope(self, scope_id: str) -> Optional[ScopeInfo]:
        """Get a scope by ID"""
        return self.scopes.get(scope_id)
        
    def find_symbol_in_scope(self, name: str, scope_id: str) -> Optional[SymbolTableEntry]:
        """Find a symbol in a specific scope"""
        scope = self.get_scope(scope_id)
        if scope:
            return scope.get_symbol(name)
        return None
        
    def find_symbol_in_scope_hierarchy(self, name: str, current_scope_id: str) -> Optional[SymbolTableEntry]:
        """Find a symbol in the scope hierarchy (current scope, then parent scopes)"""
        current_scope = self.get_scope(current_scope_id)
        while current_scope:
            symbol = current_scope.get_symbol(name)
            if symbol:
                return symbol
            # Move to parent scope
            if current_scope.parent_scope_id:
                current_scope = self.get_scope(current_scope.parent_scope_id)
            else:
                break
        
        # Special case: if we're in Main scope, also check Function and Procedure scopes
        if current_scope_id and self.get_scope(current_scope_id).scope_type == ScopeType.MAIN:
            # Check Function scope
            for scope_id, scope in self.scopes.items():
                if scope.scope_type == ScopeType.FUNCTION:
                    symbol = scope.get_symbol(name)
                    if symbol:
                        return symbol
                elif scope.scope_type == ScopeType.PROCEDURE:
                    symbol = scope.get_symbol(name)
                    if symbol:
                        return symbol
        
        return None


class SemanticError:
    """Represents a semantic error"""
    
    def __init__(self, error_type: str, message: str, node_id: int, line: int = 0):
        self.error_type = error_type
        self.message = message
        self.node_id = node_id
        self.line = line
        
    def __repr__(self):
        return f"SemanticError({self.error_type}: {self.message} at node {self.node_id})"


class ScopeAnalyzer:
    """Tree-crawling scope analyzer for SPL"""
    
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.errors: List[SemanticError] = []
        self.current_scope_id: Optional[str] = None
        self.everywhere_scope_id: Optional[str] = None
        self.global_scope_id: Optional[str] = None
        
    def analyze(self, ast) -> Tuple[bool, List[SemanticError]]:
        """
        Analyze the AST for scope violations and semantic errors.
        
        Returns:
            Tuple of (success, errors)
        """
        self.errors.clear()
        
        if not ast or ast[0] != 'SPL_PROG':
            self.errors.append(SemanticError("SYNTAX_ERROR", "Invalid AST root", 0))
            return False, self.errors
            
        try:
            self._analyze_spl_prog(ast)
            return len(self.errors) == 0, self.errors
        except Exception as e:
            import traceback
            self.errors.append(SemanticError("ANALYSIS_ERROR", f"Analysis failed: {str(e)}\n{traceback.format_exc()}", 0))
            return False, self.errors
            
    def _analyze_spl_prog(self, node):
        """Analyze SPL_PROG node"""
        # Create Everywhere scope
        self.everywhere_scope_id = self.symbol_table.get_next_scope_id()
        everywhere_scope = ScopeInfo(self.everywhere_scope_id, ScopeType.EVERYWHERE)
        self.symbol_table.add_scope(everywhere_scope)
        self.current_scope_id = self.everywhere_scope_id
        
        # Create Global scope
        self.global_scope_id = self.symbol_table.get_next_scope_id()
        global_scope = ScopeInfo(self.global_scope_id, ScopeType.GLOBAL, self.everywhere_scope_id)
        self.symbol_table.add_scope(global_scope)
        
        # Create Procedure scope
        procedure_scope_id = self.symbol_table.get_next_scope_id()
        procedure_scope = ScopeInfo(procedure_scope_id, ScopeType.PROCEDURE, self.global_scope_id)
        self.symbol_table.add_scope(procedure_scope)
        
        # Create Function scope
        function_scope_id = self.symbol_table.get_next_scope_id()
        function_scope = ScopeInfo(function_scope_id, ScopeType.FUNCTION, self.global_scope_id)
        self.symbol_table.add_scope(function_scope)
        
        # Create Main scope (with global scope as parent for variable access)
        main_scope_id = self.symbol_table.get_next_scope_id()
        main_scope = ScopeInfo(main_scope_id, ScopeType.MAIN, self.global_scope_id)
        self.symbol_table.add_scope(main_scope)
        
        # Analyze each section
        variables = node[2]  # VARIABLES (node[1] is now node_id)
        procdefs = node[3]  # PROCDEFS
        funcdefs = node[4]  # FUNCDEFS
        mainprog = node[5]  # MAINPROG
        
        # Analyze global variables
        self._analyze_variables(variables, self.global_scope_id)
        
        # Analyze procedures
        self._analyze_procdefs(procdefs, procedure_scope_id)
        
        # Analyze functions
        self._analyze_funcdefs(funcdefs, function_scope_id)
        
        # Analyze main program
        self._analyze_mainprog(mainprog, main_scope_id)
        
        # Check name identity restrictions in Everywhere scope
        self._check_everywhere_name_restrictions()
        
    def _analyze_variables(self, variables, scope_id):
        """Analyze VARIABLES node"""
        if not variables:
            return
            
        # Check for duplicate variable names in the same scope
        seen_names = set()
        for var in variables:
            if var[0] == 'VAR':
                var_name = var[2]  # var[1] is now node_id, var[2] is the name
                if var_name in seen_names:
                    node_id = var[1]  # Use the node ID from the AST
                    self.errors.append(SemanticError(
                        "NAME_RULE_VIOLATION", 
                        f"Duplicate variable name '{var_name}' in same scope", 
                        node_id
                    ))
                else:
                    seen_names.add(var_name)
                    # Add to symbol table
                    entry = SymbolTableEntry(
                        var_name, SymbolType.VARIABLE, 
                        self.symbol_table.get_scope(scope_id).scope_type,
                        var[1], scope_id, var[1]  # Use node ID from AST
                    )
                    self.symbol_table.add_entry(entry)
                    self.symbol_table.get_scope(scope_id).add_symbol(entry)
                    
    def _analyze_procdefs(self, procdefs, scope_id):
        """Analyze PROCDEFS node"""
        if not procdefs:
            return
            
        # Check for duplicate procedure names
        seen_names = set()
        for pdef in procdefs:
            if pdef[0] == 'PDEF':
                proc_name = pdef[2][2]  # NAME from PDEF (pdef[2] is name, name[2] is the actual name)
                if proc_name in seen_names:
                    node_id = pdef[1]  # Use node ID from AST
                    self.errors.append(SemanticError(
                        "NAME_RULE_VIOLATION",
                        f"Duplicate procedure name '{proc_name}' in same scope",
                        node_id
                    ))
                else:
                    seen_names.add(proc_name)
                    # Add procedure to symbol table
                    entry = SymbolTableEntry(
                        proc_name, SymbolType.PROCEDURE,
                        ScopeType.PROCEDURE, pdef[1], scope_id, pdef[1]
                    )
                    self.symbol_table.add_entry(entry)
                    self.symbol_table.get_scope(scope_id).add_symbol(entry)
                    
                    # Analyze procedure body
                    self._analyze_pdef(pdef, scope_id)
                    
    def _analyze_funcdefs(self, funcdefs, scope_id):
        """Analyze FUNCDEFS node"""
        if not funcdefs:
            return
            
        # Check for duplicate function names
        seen_names = set()
        for fdef in funcdefs:
            if fdef[0] == 'FDEF':
                func_name = fdef[2][2]  # NAME from FDEF (fdef[2] is name, name[2] is the actual name)
                if func_name in seen_names:
                    node_id = fdef[1]  # Use node ID from AST
                    self.errors.append(SemanticError(
                        "NAME_RULE_VIOLATION",
                        f"Duplicate function name '{func_name}' in same scope",
                        node_id
                    ))
                else:
                    seen_names.add(func_name)
                    # Add function to symbol table
                    entry = SymbolTableEntry(
                        func_name, SymbolType.FUNCTION,
                        ScopeType.FUNCTION, fdef[1], scope_id, fdef[1]
                    )
                    self.symbol_table.add_entry(entry)
                    self.symbol_table.get_scope(scope_id).add_symbol(entry)
                    
                    # Analyze function body
                    self._analyze_fdef(fdef, scope_id)
                    
    def _analyze_mainprog(self, mainprog, scope_id):
        """Analyze MAINPROG node"""
        if mainprog[0] == 'MAINPROG':
            variables = mainprog[2]  # mainprog[1] is now node_id
            algo = mainprog[3]
            
            # Analyze main program variables
            self._analyze_variables(variables, scope_id)
            
            # Analyze main program algorithm
            self._analyze_algo(algo, scope_id)
            
    def _analyze_pdef(self, pdef, parent_scope_id):
        """Analyze PDEF node"""
        if pdef[0] == 'PDEF':
            name = pdef[2]  # pdef[1] is node_id
            param = pdef[3]
            body = pdef[4]
            
            # Create local scope for procedure
            local_scope_id = self.symbol_table.get_next_scope_id()
            local_scope = ScopeInfo(local_scope_id, ScopeType.LOCAL, parent_scope_id)
            self.symbol_table.add_scope(local_scope)
            
            # Analyze parameters
            self._analyze_param(param, local_scope_id)
            
            # Analyze body
            self._analyze_body(body, local_scope_id)
            
    def _analyze_fdef(self, fdef, parent_scope_id):
        """Analyze FDEF node"""
        if fdef[0] == 'FDEF':
            name = fdef[2]  # fdef[1] is node_id
            param = fdef[3]
            body = fdef[4]
            return_atom = fdef[5]
            
            # Create local scope for function
            local_scope_id = self.symbol_table.get_next_scope_id()
            local_scope = ScopeInfo(local_scope_id, ScopeType.LOCAL, parent_scope_id)
            self.symbol_table.add_scope(local_scope)
            
            # Analyze parameters
            self._analyze_param(param, local_scope_id)
            
            # Analyze body
            self._analyze_body(body, local_scope_id)
            
            # Analyze return expression
            self._analyze_atom(return_atom, local_scope_id)
            
    def _analyze_param(self, param, scope_id):
        """Analyze PARAM node"""
        if param[0] == 'PARAM':
            maxthree = param[2]  # param[1] is node_id
            self._analyze_maxthree(maxthree, scope_id)
            
    def _analyze_body(self, body, scope_id):
        """Analyze BODY node"""
        if body[0] == 'BODY':
            # The body structure can be either:
            # ('BODY', [local_vars], [algo]) for functions
            # ('BODY', node_id, [local_vars], [algo]) for procedures
            if len(body) == 3:  # Function body: ('BODY', [local_vars], [algo])
                maxthree = body[1]  # Local variables list
                algo = body[2]      # Algorithm list
            else:  # Procedure body: ('BODY', node_id, [local_vars], [algo])
                maxthree = body[2]  # Local variables list
                algo = body[3]      # Algorithm list
            
            # Analyze local variables
            self._analyze_maxthree(maxthree, scope_id)
            
            # Check for parameter shadowing by local variables
            self._check_parameter_shadowing(maxthree, scope_id)
            
            # Analyze algorithm
            self._analyze_algo(algo, scope_id)
            
    def _analyze_maxthree(self, maxthree, scope_id):
        """Analyze MAXTHREE node"""
        if not maxthree:
            return
            
        # Check for duplicate variable names in the same scope
        seen_names = set()
        for var in maxthree:
            if var[0] == 'VAR':
                var_name = var[2]  # var[1] is node_id, var[2] is the name
                if var_name in seen_names:
                    node_id = var[1]  # Use node ID from AST
                    self.errors.append(SemanticError(
                        "NAME_RULE_VIOLATION",
                        f"Duplicate variable name '{var_name}' in same scope",
                        node_id
                    ))
                else:
                    seen_names.add(var_name)
                    # Add to symbol table
                    entry = SymbolTableEntry(
                        var_name, SymbolType.VARIABLE,
                        self.symbol_table.get_scope(scope_id).scope_type,
                        var[1], scope_id, var[1]  # Use node ID from AST
                    )
                    self.symbol_table.add_entry(entry)
                    self.symbol_table.get_scope(scope_id).add_symbol(entry)
                    
    def _check_parameter_shadowing(self, maxthree, scope_id):
        """Check if local variables shadow parameters"""
        if not maxthree:
            return
            
        # Get the scope and its parent to find parameters
        scope = self.symbol_table.get_scope(scope_id)
        if not scope or not scope.parent_scope_id:
            return
            
        # Find parameters in parent scope (this is a simplified approach)
        # In a real implementation, we'd need to track parameter scope more carefully
        parent_scope = self.symbol_table.get_scope(scope.parent_scope_id)
        if parent_scope:
            for var in maxthree:
                if var[0] == 'VAR':
                    var_name = var[2]  # var[1] is node_id, var[2] is the name
                    # Check if this local variable name matches any parameter
                    if parent_scope.has_symbol(var_name):
                        node_id = var[1]  # Use node ID from AST
                        self.errors.append(SemanticError(
                            "NAME_RULE_VIOLATION",
                            f"Local variable '{var_name}' shadows parameter",
                            node_id
                        ))
                        
    def _analyze_algo(self, algo, scope_id):
        """Analyze ALGO node"""
        if not algo:
            return
            
        for instr in algo:
            self._analyze_instr(instr, scope_id)
            
    def _analyze_instr(self, instr, scope_id):
        """Analyze INSTR node"""
        if not instr:
            return
            
        instr_type = instr[0]
        
        if instr_type == 'INSTR_HALT':
            pass  # No variables to analyze
        elif instr_type == 'INSTR_PRINT':
            output = instr[1]
            self._analyze_output(output, scope_id)
        elif instr_type == 'INSTR_CALL':
            name = instr[1]
            input_args = instr[2]
            self._analyze_name(name, scope_id)
            self._analyze_input(input_args, scope_id)
        elif instr_type.startswith('ASSIGN_'):
            self._analyze_assign(instr, scope_id)
        elif instr_type.startswith('LOOP_'):
            self._analyze_loop(instr, scope_id)
        elif instr_type.startswith('BRANCH_'):
            self._analyze_branch(instr, scope_id)
            
    def _analyze_assign(self, assign, scope_id):
        """Analyze ASSIGN node"""
        if assign[0] == 'ASSIGN_CALL':
            var = assign[1]
            name = assign[2]
            input_args = assign[3]
            self._analyze_var(var, scope_id)
            self._analyze_name(name, scope_id)
            self._analyze_input(input_args, scope_id)
        elif assign[0] == 'ASSIGN_TERM':
            var = assign[1]
            term = assign[2]
            self._analyze_var(var, scope_id)
            self._analyze_term(term, scope_id)
            
    def _analyze_loop(self, loop, scope_id):
        """Analyze LOOP node"""
        if loop[0] == 'LOOP_WHILE':
            term = loop[1]
            algo = loop[2]
            self._analyze_term(term, scope_id)
            self._analyze_algo(algo, scope_id)
        elif loop[0] == 'LOOP_DO_UNTIL':
            algo = loop[1]
            term = loop[2]
            self._analyze_algo(algo, scope_id)
            self._analyze_term(term, scope_id)
            
    def _analyze_branch(self, branch, scope_id):
        """Analyze BRANCH node"""
        if branch[0] == 'BRANCH_IF':
            term = branch[1]
            algo = branch[2]
            self._analyze_term(term, scope_id)
            self._analyze_algo(algo, scope_id)
        elif branch[0] == 'BRANCH_IF_ELSE':
            term = branch[1]
            algo1 = branch[2]
            algo2 = branch[3]
            self._analyze_term(term, scope_id)
            self._analyze_algo(algo1, scope_id)
            self._analyze_algo(algo2, scope_id)
            
    def _analyze_output(self, output, scope_id):
        """Analyze OUTPUT node"""
        if output[0] == 'OUTPUT_ATOM':
            atom = output[1]
            self._analyze_atom(atom, scope_id)
        elif output[0] == 'OUTPUT_STRING':
            pass  # String literals don't need scope analysis
            
    def _analyze_input(self, input_args, scope_id):
        """Analyze INPUT node"""
        if not input_args:
            return
        for atom in input_args:
            self._analyze_atom(atom, scope_id)
            
    def _analyze_term(self, term, scope_id):
        """Analyze TERM node"""
        if term[0] == 'TERM_ATOM':
            atom = term[1]
            self._analyze_atom(atom, scope_id)
        elif term[0] == 'TERM_UNOP':
            unop = term[1]
            sub_term = term[2]
            self._analyze_term(sub_term, scope_id)
        elif term[0] == 'TERM_BINOP':
            term1 = term[1]
            binop = term[2]
            term2 = term[3]
            self._analyze_term(term1, scope_id)
            self._analyze_term(term2, scope_id)
            
    def _analyze_atom(self, atom, scope_id):
        """Analyze ATOM node"""
        if atom[0] == 'ATOM_VAR':
            var = atom[2]  # atom[1] is node_id, atom[2] is the VAR tuple
            self._analyze_var(var, scope_id)
        elif atom[0] == 'ATOM_NUM':
            pass  # Numbers don't need scope analysis
            
    def _analyze_var(self, var, scope_id):
        """Analyze VAR node - this is where we check for undeclared variables"""
        if var[0] == 'VAR':
            var_name = var[2]  # var[1] is node_id, var[2] is the name
            
            # Try to find the variable in the scope hierarchy
            symbol = self.symbol_table.find_symbol_in_scope_hierarchy(var_name, scope_id)
            
            if not symbol:
                node_id = var[1]  # Use node ID from AST
                self.errors.append(SemanticError(
                    "UNDECLARED_VARIABLE",
                    f"Undeclared variable '{var_name}'",
                    node_id
                ))
            else:
                # Update symbol table with reference
                entry = SymbolTableEntry(
                    var_name, symbol.symbol_type, symbol.scope_type,
                    var[1], scope_id, symbol.declaration_node_id
                )
                self.symbol_table.add_entry(entry)
                
    def _analyze_name(self, name, scope_id):
        """Analyze NAME node"""
        if name[0] == 'NAME':
            name_value = name[2]  # name[1] is node_id, name[2] is the actual name
            # For procedure/function calls, we need to check if the name exists
            # This is a simplified check - in a real implementation, we'd need
            # to distinguish between procedure and function calls
            symbol = self.symbol_table.find_symbol_in_scope_hierarchy(name_value, scope_id)
            if not symbol:
                node_id = name[1]  # Use node ID from AST
                self.errors.append(SemanticError(
                    "UNDECLARED_VARIABLE",
                    f"Undeclared procedure/function '{name_value}'",
                    node_id
                ))
                
    def _check_everywhere_name_restrictions(self):
        """Check name identity restrictions in Everywhere scope"""
        if not self.everywhere_scope_id:
            return
            
        # Get all symbols from all scopes
        all_symbols = {}
        for scope_id, scope in self.symbol_table.scopes.items():
            for name, symbol in scope.symbols.items():
                if name not in all_symbols:
                    all_symbols[name] = []
                all_symbols[name].append(symbol)
                
        # Check for conflicts between variable names and procedure/function names
        for name, symbols in all_symbols.items():
            if len(symbols) > 1:
                # Check for conflicts
                has_variable = any(s.symbol_type == SymbolType.VARIABLE for s in symbols)
                has_procedure = any(s.symbol_type == SymbolType.PROCEDURE for s in symbols)
                has_function = any(s.symbol_type == SymbolType.FUNCTION for s in symbols)
                
                if has_variable and has_procedure:
                    node_id = self.symbol_table.get_next_node_id()
                    self.errors.append(SemanticError(
                        "NAME_RULE_VIOLATION",
                        f"Variable name '{name}' conflicts with procedure name",
                        node_id
                    ))
                    
                if has_variable and has_function:
                    node_id = self.symbol_table.get_next_node_id()
                    self.errors.append(SemanticError(
                        "NAME_RULE_VIOLATION",
                        f"Variable name '{name}' conflicts with function name",
                        node_id
                    ))
                    
                if has_procedure and has_function:
                    node_id = self.symbol_table.get_next_node_id()
                    self.errors.append(SemanticError(
                        "NAME_RULE_VIOLATION",
                        f"Procedure name '{name}' conflicts with function name",
                        node_id
                    ))


def analyze_spl_semantics(ast) -> Tuple[bool, List[SemanticError]]:
    """
    Analyze SPL AST for semantic errors.
    
    Args:
        ast: Abstract Syntax Tree from parser
        
    Returns:
        Tuple of (success, errors)
    """
    analyzer = ScopeAnalyzer()
    return analyzer.analyze(ast)


def print_semantic_errors(errors: List[SemanticError]):
    """Print semantic errors in a readable format"""
    if not errors:
        print("OK: No semantic errors found")
        return
        
    print(f"ERROR: Found {len(errors)} semantic error(s):")
    for i, error in enumerate(errors, 1):
        print(f"  {i}. {error.error_type}: {error.message}")


if __name__ == "__main__":
    # Test the semantic analyzer
    from parser import parse_spl
    
    # Test with a simple program
    test_program = """
    glob { x y }
    proc { }
    func { }
    main {
        var { a }
        x = 10;
        y = 20;
        a = 5;
        halt
    """
    
    print("=" * 80)
    print("SPL Semantic Analyzer Test")
    print("=" * 80)
    
    ast = parse_spl(test_program)
    if ast:
        success, errors = analyze_spl_semantics(ast)
        print_semantic_errors(errors)
        if success:
            print("\n✓ Semantic analysis completed successfully!")
        else:
            print(f"\n✗ Semantic analysis found {len(errors)} error(s)")
    else:
        print("✗ Parsing failed")
