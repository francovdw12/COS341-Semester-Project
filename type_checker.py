"""
Type Checker for SPL Compiler
Implements syntax-based type analysis according to the semantic attribution rules.
"""

from enum import Enum
from typing import Dict, List, Tuple, Optional, Any
import traceback

class TypeCheckerErrorType(Enum):
    """Types of type checking errors"""
    TYPE_MISMATCH = "TYPE_MISMATCH"
    INVALID_OPERATION = "INVALID_OPERATION"
    UNDECLARED_TYPE = "UNDECLARED_TYPE"
    INVALID_RETURN_TYPE = "INVALID_RETURN_TYPE"
    INVALID_CONDITION_TYPE = "INVALID_CONDITION_TYPE"
    INVALID_ASSIGNMENT_TYPE = "INVALID_ASSIGNMENT_TYPE"

class TypeCheckerError:
    """Represents a type checking error"""
    def __init__(self, error_type: TypeCheckerErrorType, message: str, node_id: Optional[int] = None, 
                 location: Optional[str] = None, context: Optional[str] = None):
        self.error_type = error_type
        self.message = message
        self.node_id = node_id
        self.location = location  # e.g., "function 'foo' at line 5"
        self.context = context   # e.g., "in assignment statement"
        self.traceback = traceback.format_exc()

class TypeChecker:
    """Type checker for SPL programs"""
    
    def __init__(self, symbol_table):
        """Initialize type checker with symbol table from scope analysis"""
        self.symbol_table = symbol_table
        self.errors = []
        self.type_cache = {}  # Cache for computed types
        
    def check_types(self, ast) -> Tuple[bool, List[TypeCheckerError]]:
        """Main entry point for type checking"""
        try:
            self.errors = []
            self.type_cache = {}
            
            # Start type checking from the root
            success = self._check_spl_prog(ast)
            
            return success, self.errors
            
        except Exception as e:
            error = TypeCheckerError(
                TypeCheckerErrorType.INVALID_OPERATION,
                f"Type checker error: {str(e)}"
            )
            self.errors.append(error)
            return False, self.errors
    
    def _add_error(self, error_type: TypeCheckerErrorType, message: str, node_id: Optional[int] = None, 
                   location: Optional[str] = None, context: Optional[str] = None):
        """Add an error to the error list"""
        error = TypeCheckerError(error_type, message, node_id, location, context)
        self.errors.append(error)
    
    def _get_node_id(self, node) -> Optional[int]:
        """Extract node ID from AST node"""
        if isinstance(node, tuple) and len(node) > 1:
            return node[1]
        return None
    
    def _get_variable_name(self, var_node) -> Optional[str]:
        """Extract variable name from VAR node"""
        if isinstance(var_node, tuple) and len(var_node) >= 3:
            return var_node[2]  # VAR node structure: ('VAR', node_id, name)
        return None
    
    def _get_function_name(self, fdef_node) -> Optional[str]:
        """Extract function name from FDEF node"""
        if isinstance(fdef_node, tuple) and len(fdef_node) >= 3:
            name_node = fdef_node[2]  # FDEF structure: ('FDEF', node_id, name, param, body, atom)
            if isinstance(name_node, tuple) and len(name_node) >= 3:
                return name_node[2]  # NAME node structure: ('NAME', node_id, name)
        return None
    
    def _get_location_info(self, node, context_type: str = "expression") -> str:
        """Generate location information for error reporting"""
        node_id = self._get_node_id(node)
        location_parts = []
        
        if context_type == "function":
            func_name = self._get_function_name(node)
            if func_name:
                location_parts.append(f"function '{func_name}'")
        elif context_type == "variable":
            var_name = self._get_variable_name(node)
            if var_name:
                location_parts.append(f"variable '{var_name}'")
        
        if node_id:
            location_parts.append(f"node {node_id}")
        
        return " at " + " ".join(location_parts) if location_parts else ""
    
    def _check_spl_prog(self, node) -> bool:
        """Check SPL_PROG: correctly typed if all components are correctly typed"""
        if node[0] != 'SPL_PROG':
            return False
            
        node_id = self._get_node_id(node)
        variables = node[2]
        procdefs = node[3]
        funcdefs = node[4]
        mainprog = node[5]
        
        # Check all components
        variables_ok = self._check_variables(variables)
        procdefs_ok = self._check_procdefs(procdefs)
        funcdefs_ok = self._check_funcdefs(funcdefs)
        mainprog_ok = self._check_mainprog(mainprog)
        
        return variables_ok and procdefs_ok and funcdefs_ok and mainprog_ok
    
    def _check_variables(self, variables) -> bool:
        """Check VARIABLES: correctly typed if all VARs are numeric"""
        if not variables:  # Empty/nullable case
            return True
        
        # Handle case where variables might be a single VAR or list
        if isinstance(variables, tuple):
            # Single VAR
            return self._check_var(variables)
        elif isinstance(variables, list):
            # List of VARs
            for var in variables:
                if not self._check_var(var):
                    return False
        return True
    
    def _check_var(self, var) -> bool:
        """Check VAR: is of type 'numeric' (fact)"""
        # All variables are implicitly numeric in SPL
        return True
    
    def _check_procdefs(self, procdefs) -> bool:
        """Check PROCDEFS: correctly typed if all PDEFs are correctly typed"""
        if not procdefs:  # Empty/nullable case
            return True
        
        # Handle case where procdefs might be a single PDEF or list
        if isinstance(procdefs, tuple):
            # Single PDEF
            return self._check_pdef(procdefs)
        elif isinstance(procdefs, list):
            # List of PDEFs
            for pdef in procdefs:
                if not self._check_pdef(pdef):
                    return False
        return True
    
    def _check_funcdefs(self, funcdefs) -> bool:
        """Check FUNCDEFS: correctly typed if all FDEFs are correctly typed"""
        if not funcdefs:  # Empty/nullable case
            return True
        
        # Handle case where funcdefs might be a single FDEF or list
        if isinstance(funcdefs, tuple):
            # Single FDEF
            return self._check_fdef(funcdefs)
        elif isinstance(funcdefs, list):
            # List of FDEFs
            for fdef in funcdefs:
                if not self._check_fdef(fdef):
                    return False
        return True
    
    def _check_pdef(self, pdef) -> bool:
        """Check PDEF: correctly typed if NAME is type-less, PARAM is correctly typed, and BODY is correctly typed"""
        if pdef[0] != 'PDEF':
            return False
            
        node_id = self._get_node_id(pdef)
        name = pdef[2]
        param = pdef[3]
        body = pdef[4]
        
        # Check if NAME is type-less (not in symbol table with conflicting type)
        name_ok = self._check_name_type_less(name, node_id)
        param_ok = self._check_param(param)
        body_ok = self._check_body(body)
        
        return name_ok and param_ok and body_ok
    
    def _check_fdef(self, fdef) -> bool:
        """Check FDEF: correctly typed if NAME is type-less, PARAM is correctly typed, BODY is correctly typed, and ATOM is numeric"""
        if fdef[0] != 'FDEF':
            return False
            
        node_id = self._get_node_id(fdef)
        name = fdef[2]
        param = fdef[3]
        body = fdef[4]
        atom = fdef[5]
        
        # Check if NAME is type-less
        name_ok = self._check_name_type_less(name, node_id)
        param_ok = self._check_param(param)
        body_ok = self._check_body(body)
        atom_ok = self._check_atom_numeric(atom)
        
        return name_ok and param_ok and body_ok and atom_ok
    
    def _check_name_type_less(self, name, node_id) -> bool:
        """Check if NAME is type-less (no conflicting type in symbol table)"""
        # For now, assume all names are type-less at declaration
        # In a more sophisticated implementation, we'd check the symbol table
        return True
    
    def _check_param(self, param) -> bool:
        """Check PARAM: correctly typed if MAXTHREE is correctly typed"""
        if param[0] != 'PARAM':
            return False
            
        maxthree = param[2]
        return self._check_maxthree(maxthree)
    
    def _check_body(self, body) -> bool:
        """Check BODY: correctly typed if MAXTHREE and ALGO are correctly typed"""
        if body[0] != 'BODY':
            return False
        
        # Handle different BODY structures
        if len(body) == 3:
            # BODY with 3 elements: (BODY, maxthree, algo)
            maxthree = body[1]
            algo = body[2]
        elif len(body) == 4:
            # BODY with 4 elements: (BODY, node_id, maxthree, algo)
            maxthree = body[2]
            algo = body[3]
        else:
            return False
        
        maxthree_ok = self._check_maxthree(maxthree)
        algo_ok = self._check_algo(algo)
        
        return maxthree_ok and algo_ok
    
    def _check_maxthree(self, maxthree) -> bool:
        """Check MAXTHREE: correctly typed if all VARs are numeric"""
        if not maxthree:  # Empty/nullable case
            return True
        
        # Handle case where maxthree might be a single VAR or list
        if isinstance(maxthree, tuple):
            # Single VAR
            return self._check_var(maxthree)
        elif isinstance(maxthree, list):
            # List of VARs
            for var in maxthree:
                if not self._check_var(var):
                    return False
        return True
    
    def _check_mainprog(self, mainprog) -> bool:
        """Check MAINPROG: correctly typed if VARIABLES and ALGO are correctly typed"""
        if mainprog[0] != 'MAINPROG':
            return False
            
        variables = mainprog[2]
        algo = mainprog[3]
        
        variables_ok = self._check_variables(variables)
        algo_ok = self._check_algo(algo)
        
        return variables_ok and algo_ok
    
    def _check_atom(self, atom) -> str:
        """Check ATOM and return its type"""
        if atom[0] == 'ATOM_VAR':
            var = atom[2]
            return self._get_var_type(var)
        elif atom[0] == 'ATOM_NUM':
            return "numeric"  # Numbers are always numeric
        else:
            return "unknown"
    
    def _check_atom_numeric(self, atom) -> bool:
        """Check if ATOM is of type 'numeric'"""
        atom_type = self._check_atom(atom)
        if atom_type != "numeric":
            node_id = self._get_node_id(atom)
            var_name = self._get_variable_name(atom) if atom[0] == 'ATOM_VAR' else None
            location = f"return statement" + (f" (variable '{var_name}')" if var_name else "")
            context = "function return value"
            self._add_error(
                TypeCheckerErrorType.INVALID_RETURN_TYPE,
                f"Function return value must be numeric, got {atom_type}",
                node_id, location, context
            )
            return False
        return True
    
    def _get_var_type(self, var) -> str:
        """Get the type of a variable"""
        if var[0] == 'VAR':
            # All variables in SPL are numeric
            return "numeric"
        return "unknown"
    
    def _check_algo(self, algo) -> bool:
        """Check ALGO: correctly typed if all INSTRs are correctly typed"""
        if not algo:  # Empty case
            return True
            
        for instr in algo:
            if not self._check_instr(instr):
                return False
        return True
    
    def _check_instr(self, instr) -> bool:
        """Check INSTR: correctly typed based on instruction type"""
        if instr[0] == 'INSTR_HALT':
            return True  # halt is always correctly typed
        elif instr[0] == 'INSTR_PRINT':
            output = instr[1]
            return self._check_output(output)
        elif instr[0] == 'INSTR_CALL':
            name = instr[1]
            input_args = instr[2]
            return self._check_name_type_less(name, None) and self._check_input(input_args)
        elif instr[0] == 'ASSIGN_CALL':
            var = instr[1]
            name = instr[2]
            input_args = instr[3]
            var_ok = self._get_var_type(var) == "numeric"
            name_ok = self._check_name_type_less(name, None)
            input_ok = self._check_input(input_args)
            return var_ok and name_ok and input_ok
        elif instr[0] == 'ASSIGN_TERM':
            var = instr[1]
            term = instr[2]
            var_ok = self._get_var_type(var) == "numeric"
            term_ok = self._check_term_numeric(term)
            return var_ok and term_ok
        elif instr[0] == 'LOOP_WHILE':
            term = instr[1]
            algo = instr[2]
            term_ok = self._check_term_boolean(term)
            algo_ok = self._check_algo(algo)
            return term_ok and algo_ok
        elif instr[0] == 'LOOP_DO_UNTIL':
            algo = instr[1]
            term = instr[2]
            algo_ok = self._check_algo(algo)
            term_ok = self._check_term_boolean(term)
            return algo_ok and term_ok
        elif instr[0] == 'BRANCH_IF':
            term = instr[1]
            algo = instr[2]
            term_ok = self._check_term_boolean(term)
            algo_ok = self._check_algo(algo)
            return term_ok and algo_ok
        elif instr[0] == 'BRANCH_IF_ELSE':
            term = instr[1]
            algo0 = instr[2]
            algo1 = instr[3]
            term_ok = self._check_term_boolean(term)
            algo0_ok = self._check_algo(algo0)
            algo1_ok = self._check_algo(algo1)
            return term_ok and algo0_ok and algo1_ok
        else:
            return False
    
    def _check_output(self, output) -> bool:
        """Check OUTPUT: correctly typed if ATOM is numeric or if string"""
        if output[0] == 'OUTPUT_ATOM':
            atom = output[1]
            return self._check_atom_numeric(atom)
        elif output[0] == 'OUTPUT_STRING':
            return True  # Strings are always correctly typed
        else:
            return False
    
    def _check_input(self, input_args) -> bool:
        """Check INPUT: correctly typed if all ATOMs are numeric"""
        if not input_args:  # Empty/nullable case
            return True
            
        for atom in input_args:
            if not self._check_atom_numeric(atom):
                return False
        return True
    
    def _check_term(self, term) -> str:
        """Check TERM and return its type"""
        if term[0] == 'TERM_ATOM':
            atom = term[1]
            return self._check_atom(atom)
        elif term[0] == 'TERM_UNOP':
            unop = term[1]
            sub_term = term[2]
            return self._check_unop_term(unop, sub_term)
        elif term[0] == 'TERM_BINOP':
            term1 = term[1]
            binop = term[2]
            term2 = term[3]
            return self._check_binop_term(term1, binop, term2)
        else:
            return "unknown"
    
    def _check_term_numeric(self, term) -> bool:
        """Check if TERM is of type 'numeric'"""
        term_type = self._check_term(term)
        if term_type != "numeric":
            node_id = self._get_node_id(term)
            location = "assignment statement"
            context = "right-hand side expression"
            self._add_error(
                TypeCheckerErrorType.TYPE_MISMATCH,
                f"Expected numeric type, got {term_type}",
                node_id, location, context
            )
            return False
        return True
    
    def _check_term_boolean(self, term) -> bool:
        """Check if TERM is of type 'boolean'"""
        term_type = self._check_term(term)
        if term_type != "boolean":
            node_id = self._get_node_id(term)
            location = "conditional statement"
            context = "condition expression"
            self._add_error(
                TypeCheckerErrorType.INVALID_CONDITION_TYPE,
                f"Expected boolean type for condition, got {term_type}",
                node_id, location, context
            )
            return False
        return True
    
    def _check_unop_term(self, unop, sub_term) -> str:
        """Check unary operation and return type"""
        unop_type = self._get_unop_type(unop)
        sub_term_type = self._check_term(sub_term)
        
        if unop_type == "numeric" and sub_term_type == "numeric":
            return "numeric"
        elif unop_type == "boolean" and sub_term_type == "boolean":
            return "boolean"
        else:
            node_id = self._get_node_id(sub_term)
            location = f"unary operator '{unop}' expression"
            context = f"operand of {unop} operator"
            self._add_error(
                TypeCheckerErrorType.TYPE_MISMATCH,
                f"Unary operator {unop} expects {unop_type}, got {sub_term_type}",
                node_id, location, context
            )
            return "unknown"
    
    def _check_binop_term(self, term1, binop, term2) -> str:
        """Check binary operation and return type"""
        binop_type = self._get_binop_type(binop)
        term1_type = self._check_term(term1)
        term2_type = self._check_term(term2)
        
        if binop_type == "numeric" and term1_type == "numeric" and term2_type == "numeric":
            return "numeric"
        elif binop_type == "boolean" and term1_type == "boolean" and term2_type == "boolean":
            return "boolean"
        elif binop_type == "comparison" and term1_type == "numeric" and term2_type == "numeric":
            return "boolean"
        else:
            node_id = self._get_node_id(term1)
            location = f"binary operator '{binop}' expression"
            context = f"operands of {binop} operator"
            self._add_error(
                TypeCheckerErrorType.TYPE_MISMATCH,
                f"Binary operator {binop} expects {binop_type} operands, got {term1_type} and {term2_type}",
                node_id, location, context
            )
            return "unknown"
    
    def _get_unop_type(self, unop) -> str:
        """Get the type of a unary operator"""
        if unop == 'NEG':
            return "numeric"
        elif unop == 'NOT':
            return "boolean"
        else:
            return "unknown"
    
    def _get_binop_type(self, binop) -> str:
        """Get the type of a binary operator"""
        if binop in ['PLUS', 'MINUS', 'MULT', 'DIV']:
            return "numeric"
        elif binop in ['OR', 'AND']:
            return "boolean"
        elif binop in ['GT', 'EQ', 'LT', 'LE', 'GE', 'NE']:
            return "comparison"
        else:
            return "unknown"

def check_spl_types(ast, symbol_table) -> Tuple[bool, List[TypeCheckerError]]:
    """Main function to check types in SPL program"""
    checker = TypeChecker(symbol_table)
    return checker.check_types(ast)

def print_type_errors(errors: List[TypeCheckerError]):
    """Print type checking errors with detailed location information"""
    if not errors:
        print("OK: No type errors found")
        return
    
    print(f"ERROR: Found {len(errors)} type error(s):")
    for i, error in enumerate(errors, 1):
        print(f"  {i}. {error.error_type.value}: {error.message}")
        
        # Add location information
        if error.location:
            print(f"     Location: {error.location}")
        
        # Add context information
        if error.context:
            print(f"     Context: {error.context}")
        
        # Add node ID for debugging
        if error.node_id:
            print(f"     Node ID: {error.node_id}")
        
        print()  # Add blank line for readability
