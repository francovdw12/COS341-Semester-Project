"""
Inlining Module for SPL Compiler
Replaces CALL instructions with actual function/procedure code by inlining.
"""

from typing import Dict, List, Tuple, Optional, Any
import re

class Inliner:
    """Inliner for replacing CALL instructions with actual code"""
    
    def __init__(self, ast, symbol_table):
        """Initialize inliner with AST and symbol table"""
        self.ast = ast
        self.symbol_table = symbol_table
        self.functions = {}  # Store function definitions
        self.procedures = {}  # Store procedure definitions
        self.inlined_code = ""
        
    def inline_code(self, intermediate_code: str) -> str:
        """Main entry point for inlining CALL instructions"""
        try:
            self.inlined_code = intermediate_code
            self._extract_definitions()
            self._inline_calls()
            return self.inlined_code
        except Exception as e:
            print(f"Inlining error: {str(e)}")
            return intermediate_code
    
    def _extract_definitions(self):
        """Extract function and procedure definitions from AST"""
        if self.ast[0] != 'SPL_PROG':
            return
        
        # Extract functions
        funcdefs = self.ast[4]
        if funcdefs:
            if isinstance(funcdefs, list):
                for fdef in funcdefs:
                    self._extract_function(fdef)
            else:
                self._extract_function(funcdefs)
        
        # Extract procedures
        procdefs = self.ast[3]
        if procdefs:
            if isinstance(procdefs, list):
                for pdef in procdefs:
                    self._extract_procedure(pdef)
            else:
                self._extract_procedure(procdefs)
    
    def _extract_function(self, fdef):
        """Extract function definition"""
        if fdef[0] != 'FDEF':
            return
        
        func_name = self._get_function_name(fdef[2])
        params = self._extract_parameters(fdef[3])
        body = fdef[4]
        return_atom = fdef[5]
        
        self.functions[func_name] = {
            'params': params,
            'body': body,
            'return': return_atom
        }
    
    def _extract_procedure(self, pdef):
        """Extract procedure definition"""
        if pdef[0] != 'PDEF':
            return
        
        proc_name = self._get_procedure_name(pdef[2])
        params = self._extract_parameters(pdef[3])
        body = pdef[4]
        
        self.procedures[proc_name] = {
            'params': params,
            'body': body
        }
    
    def _extract_parameters(self, param_node):
        """Extract parameter names from PARAM node"""
        if param_node[0] != 'PARAM':
            return []
        
        maxthree = param_node[2]
        if not maxthree:
            return []
        
        params = []
        for var in maxthree:
            if var[0] == 'VAR':
                params.append(var[2])  # Parameter name
        return params
    
    def _get_function_name(self, name_node):
        """Extract function name from NAME node"""
        if isinstance(name_node, tuple) and len(name_node) >= 3:
            return name_node[2]
        return "unknown"
    
    def _get_procedure_name(self, name_node):
        """Extract procedure name from NAME node"""
        if isinstance(name_node, tuple) and len(name_node) >= 3:
            return name_node[2]
        return "unknown"
    
    def _inline_calls(self):
        """Replace all CALL instructions with inlined code"""
        lines = self.inlined_code.split('\n')
        new_lines = []
        
        for line in lines:
            if 'CALL' in line:
                # Parse the CALL instruction
                if '=' in line:
                    # Function call with assignment
                    var_name, call_part = line.split(' = ', 1)
                    call_part = call_part.strip()
                    inlined_code = self._inline_function_call(var_name, call_part)
                    if inlined_code:
                        new_lines.extend(inlined_code.split('\n'))
                    else:
                        new_lines.append(line)  # Keep original if inlining fails
                else:
                    # Procedure call
                    call_part = line.strip()
                    inlined_code = self._inline_procedure_call(call_part)
                    if inlined_code:
                        new_lines.extend(inlined_code.split('\n'))
                    else:
                        new_lines.append(line)  # Keep original if inlining fails
            else:
                new_lines.append(line)
        
        self.inlined_code = '\n'.join(new_lines)
    
    def _inline_function_call(self, var_name: str, call_part: str) -> str:
        """Inline a function call with assignment"""
        # Parse: CALL function_name(arg1, arg2, ...)
        match = re.match(r'CALL\s+(\w+)\s*\((.*)\)', call_part)
        if not match:
            return ""
        
        func_name = match.group(1)
        args_str = match.group(2).strip()
        
        if func_name not in self.functions:
            return ""
        
        func_def = self.functions[func_name]
        params = func_def['params']
        body = func_def['body']
        return_atom = func_def['return']
        
        # Parse arguments
        args = [arg.strip() for arg in args_str.split(',')] if args_str else []
        
        # Create parameter mapping
        param_map = {}
        for i, param in enumerate(params):
            if i < len(args):
                param_map[param] = args[i]
        
        # Generate inlined code
        inlined_lines = []
        
        # Inline the function body
        body_code = self._inline_body(body, param_map)
        if body_code:
            inlined_lines.extend(body_code.split('\n'))
        
        # Add the return assignment
        return_var = self._get_atom_name(return_atom)
        if return_var:
            inlined_lines.append(f"{var_name} = {return_var}")
        
        return '\n'.join(inlined_lines)
    
    def _inline_procedure_call(self, call_part: str) -> str:
        """Inline a procedure call"""
        # Parse: CALL procedure_name(arg1, arg2, ...)
        match = re.match(r'CALL\s+(\w+)\s*\((.*)\)', call_part)
        if not match:
            return ""
        
        proc_name = match.group(1)
        args_str = match.group(2).strip()
        
        if proc_name not in self.procedures:
            return ""
        
        proc_def = self.procedures[proc_name]
        params = proc_def['params']
        body = proc_def['body']
        
        # Parse arguments
        args = [arg.strip() for arg in args_str.split(',')] if args_str else []
        
        # Create parameter mapping
        param_map = {}
        for i, param in enumerate(params):
            if i < len(args):
                param_map[param] = args[i]
        
        # Generate inlined code
        body_code = self._inline_body(body, param_map)
        return body_code
    
    def _inline_body(self, body, param_map: Dict[str, str]) -> str:
        """Inline a function/procedure body with parameter substitution"""
        if body[0] != 'BODY':
            return ""
        
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
            return ""
        
        # Generate local variable declarations (if any)
        local_vars = []
        if maxthree:
            for var in maxthree:
                if var[0] == 'VAR':
                    var_name = var[2]
                    local_vars.append(var_name)
        
        # Generate algorithm code
        algo_code = self._generate_algo_code(algo, param_map)
        
        # Combine local variables and algorithm
        result_lines = []
        if local_vars:
            # Local variables are typically not needed in intermediate code
            # as they're handled by the symbol table, but we can add them as comments
            result_lines.append(f"// Local variables: {', '.join(local_vars)}")
        
        if algo_code:
            result_lines.extend(algo_code.split('\n'))
        
        return '\n'.join(result_lines)
    
    def _generate_algo_code(self, algo, param_map: Dict[str, str]) -> str:
        """Generate code for algorithm with parameter substitution"""
        if not algo:
            return ""
        
        lines = []
        for instr in algo:
            instr_code = self._generate_instruction(instr, param_map)
            if instr_code:
                lines.append(instr_code)
        
        return '\n'.join(lines)
    
    def _generate_instruction(self, instr, param_map: Dict[str, str]) -> str:
        """Generate code for individual instruction with parameter substitution"""
        if not instr:
            return ""
        
        instr_type = instr[0]
        
        if instr_type == 'INSTR_HALT':
            return "STOP"
        elif instr_type == 'INSTR_PRINT':
            return self._generate_print_with_params(instr[1], param_map)
        elif instr_type == 'INSTR_CALL':
            return self._generate_procedure_call_with_params(instr[1], instr[2], param_map)
        elif instr_type == 'ASSIGN_CALL':
            return self._generate_function_call_with_params(instr[1], instr[2], instr[3], param_map)
        elif instr_type == 'ASSIGN_TERM':
            return self._generate_assignment_with_params(instr[1], instr[2], param_map)
        elif instr_type == 'LOOP_WHILE':
            return self._generate_while_loop_with_params(instr[1], instr[2], param_map)
        elif instr_type == 'LOOP_DO_UNTIL':
            return self._generate_do_until_loop_with_params(instr[1], instr[2], param_map)
        elif instr_type == 'BRANCH_IF':
            return self._generate_if_then_with_params(instr[1], instr[2], param_map)
        elif instr_type == 'BRANCH_IF_ELSE':
            return self._generate_if_else_with_params(instr[1], instr[2], instr[3], param_map)
        
        return ""
    
    def _generate_print_with_params(self, output, param_map: Dict[str, str]) -> str:
        """Generate print statement with parameter substitution"""
        if output[0] == 'OUTPUT_STRING':
            string_value = output[1]
            return f'PRINT "{string_value}"'
        elif output[0] == 'OUTPUT_ATOM':
            atom = output[1]
            atom_name = self._get_atom_name(atom)
            if atom_name in param_map:
                atom_name = param_map[atom_name]
            return f"PRINT {atom_name}"
        return ""
    
    def _generate_assignment_with_params(self, var, term, param_map: Dict[str, str]) -> str:
        """Generate assignment with parameter substitution"""
        var_name = self._get_variable_name(var)
        if var_name in param_map:
            var_name = param_map[var_name]
        
        term_code = self._generate_term_with_params(term, param_map)
        return f"{var_name} = {term_code}"
    
    def _generate_term_with_params(self, term, param_map: Dict[str, str]) -> str:
        """Generate term expression with parameter substitution"""
        if term[0] == 'TERM_ATOM':
            atom = term[1]
            atom_name = self._get_atom_name(atom)
            if atom_name in param_map:
                atom_name = param_map[atom_name]
            return atom_name
        elif term[0] == 'TERM_UNOP':
            unop = term[1]
            sub_term = term[2]
            sub_term_code = self._generate_term_with_params(sub_term, param_map)
            if unop == 'NEG':
                return f"-{sub_term_code}"
            return sub_term_code
        elif term[0] == 'TERM_BINOP':
            term1 = term[1]
            binop = term[2]
            term2 = term[3]
            term1_code = self._generate_term_with_params(term1, param_map)
            term2_code = self._generate_term_with_params(term2, param_map)
            
            op_map = {
                'EQ': '=',
                'GT': '>',
                'PLUS': '+',
                'MINUS': '-',
                'MULT': '*',
                'DIV': '/'
            }
            operator = op_map.get(binop, binop)
            return f"({term1_code} {operator} {term2_code})"
        
        return "0"
    
    def _generate_procedure_call_with_params(self, name, input_args, param_map: Dict[str, str]) -> str:
        """Generate procedure call with parameter substitution"""
        name_str = self._get_function_name(name)
        args = []
        for arg in input_args:
            if arg[0] == 'ATOM_NUM':
                args.append(str(arg[2]))
            elif arg[0] == 'ATOM_VAR':
                var = arg[2]
                var_name = self._get_variable_name(var)
                if var_name in param_map:
                    var_name = param_map[var_name]
                args.append(var_name)
        
        args_str = ", ".join(args)
        return f"CALL {name_str}({args_str})"
    
    def _generate_function_call_with_params(self, var, name, input_args, param_map: Dict[str, str]) -> str:
        """Generate function call with parameter substitution"""
        var_name = self._get_variable_name(var)
        if var_name in param_map:
            var_name = param_map[var_name]
        
        name_str = self._get_function_name(name)
        args = []
        for arg in input_args:
            if arg[0] == 'ATOM_NUM':
                args.append(str(arg[2]))
            elif arg[0] == 'ATOM_VAR':
                var = arg[2]
                var_name = self._get_variable_name(var)
                if var_name in param_map:
                    var_name = param_map[var_name]
                args.append(var_name)
        
        args_str = ", ".join(args)
        return f"{var_name} = CALL {name_str}({args_str})"
    
    def _generate_while_loop_with_params(self, condition, loop_algo, param_map: Dict[str, str]) -> str:
        """Generate while loop with parameter substitution"""
        condition_code = self._generate_term_with_params(condition, param_map)
        loop_code = self._generate_algo_code(loop_algo, param_map)
        
        label_loop = "L_LOOP"
        label_exit = "L_EXIT"
        
        lines = [
            f"REM {label_loop}",
            f"IF {condition_code} = 0 THEN {label_exit}",
            loop_code,
            f"GOTO {label_loop}",
            f"REM {label_exit}"
        ]
        
        return '\n'.join(lines)
    
    def _generate_do_until_loop_with_params(self, loop_algo, condition, param_map: Dict[str, str]) -> str:
        """Generate do-until loop with parameter substitution"""
        condition_code = self._generate_term_with_params(condition, param_map)
        loop_code = self._generate_algo_code(loop_algo, param_map)
        
        label_loop = "L_LOOP"
        label_exit = "L_EXIT"
        
        lines = [
            f"REM {label_loop}",
            loop_code,
            f"IF {condition_code} = 1 THEN {label_exit}",
            f"GOTO {label_loop}",
            f"REM {label_exit}"
        ]
        
        return '\n'.join(lines)
    
    def _generate_if_then_with_params(self, condition, then_algo, param_map: Dict[str, str]) -> str:
        """Generate if-then with parameter substitution"""
        condition_code = self._generate_term_with_params(condition, param_map)
        then_code = self._generate_algo_code(then_algo, param_map)
        
        label_then = "L_THEN"
        label_exit = "L_EXIT"
        
        lines = [
            f"IF {condition_code} = 1 THEN {label_then}",
            f"GOTO {label_exit}",
            f"REM {label_then}",
            then_code,
            f"REM {label_exit}"
        ]
        
        return '\n'.join(lines)
    
    def _generate_if_else_with_params(self, condition, then_algo, else_algo, param_map: Dict[str, str]) -> str:
        """Generate if-else with parameter substitution"""
        condition_code = self._generate_term_with_params(condition, param_map)
        then_code = self._generate_algo_code(then_algo, param_map)
        else_code = self._generate_algo_code(else_algo, param_map)
        
        label_then = "L_THEN"
        label_exit = "L_EXIT"
        
        lines = [
            f"IF {condition_code} = 1 THEN {label_then}",
            else_code,
            f"GOTO {label_exit}",
            f"REM {label_then}",
            then_code,
            f"REM {label_exit}"
        ]
        
        return '\n'.join(lines)
    
    def _get_variable_name(self, var_node):
        """Extract variable name from VAR node"""
        if isinstance(var_node, tuple) and len(var_node) >= 3:
            return var_node[2]
        return "unknown"
    
    def _get_atom_name(self, atom):
        """Extract name from ATOM node"""
        if atom[0] == 'ATOM_NUM':
            return str(atom[2])
        elif atom[0] == 'ATOM_VAR':
            var = atom[2]
            return self._get_variable_name(var)
        return "unknown"


def inline_intermediate_code(ast, symbol_table, intermediate_code: str, output_filename: str = "inlined_code.txt") -> str:
    """
    Main function to inline CALL instructions in intermediate code
    
    Args:
        ast: Abstract Syntax Tree from parser
        symbol_table: Symbol table from scope analysis
        intermediate_code: Generated intermediate code
        output_filename: Name of output file for inlined code
        
    Returns:
        Inlined intermediate code as string
    """
    inliner = Inliner(ast, symbol_table)
    inlined_code = inliner.inline_code(intermediate_code)
    
    try:
        with open(output_filename, 'w', encoding='ascii') as f:
            f.write(inlined_code)
        print(f"Inlined code saved to {output_filename}")
    except Exception as e:
        print(f"Error saving inlined code: {str(e)}")
    
    return inlined_code


if __name__ == "__main__":
    print("Inlining Module for SPL Compiler")
    print("This module replaces CALL instructions with actual function/procedure code.")
