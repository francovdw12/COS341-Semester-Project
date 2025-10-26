"""
Intermediate Code Generator for SPL Compiler
Implements code generation according to the specification for intermediate code generation.
"""

from typing import Dict, List, Tuple, Optional, Any
import os

class CodeGenerator:
    """Intermediate code generator for SPL programs"""
    
    def __init__(self, symbol_table):
        """Initialize code generator with symbol table from scope analysis"""
        self.symbol_table = symbol_table
        self.target_code = ""
        self.label_counter = 0
        self.temp_counter = 0
        
    def generate_code(self, ast) -> str:
        """Main entry point for code generation"""
        try:
            self.target_code = ""
            self.label_counter = 0
            self.temp_counter = 0
            
            # Generate code for the main program
            self._generate_spl_prog(ast)
            
            return self.target_code
            
        except Exception as e:
            print(f"Code generation error: {str(e)}")
            return ""
    
    def _get_next_label(self) -> str:
        """Generate next unique label"""
        self.label_counter += 1
        return f"L{self.label_counter}"
    
    def _get_next_temp(self) -> str:
        """Generate next unique temporary variable"""
        self.temp_counter += 1
        return f"T{self.temp_counter}"
    
    def _append_code(self, code: str):
        """Append code to target code with newline"""
        if self.target_code:
            self.target_code += "\n"
        self.target_code += code
    
    def _generate_spl_prog(self, node):
        """Generate code for SPL_PROG"""
        if node[0] != 'SPL_PROG':
            return
        
        # Only generate code for the main program
        # Variables, procedures, and functions are handled separately
        mainprog = node[5]
        self._generate_mainprog(mainprog)
    
    def _generate_mainprog(self, node):
        """Generate code for MAINPROG - only ALGO part gets translated"""
        if node[0] != 'MAINPROG':
            return
        
        # Variables are not translated - they were only for symbol table
        # Only generate code for the ALGO part
        algo = node[3]
        self._generate_algo(algo)
    
    def _generate_algo(self, algo):
        """Generate code for ALGO (sequence of instructions)"""
        if not algo:
            return
        
        # Handle sequential execution
        for instr in algo:
            self._generate_instr(instr)
    
    def _generate_instr(self, instr):
        """Generate code for individual instruction"""
        if not instr:
            return
        
        instr_type = instr[0]
        
        if instr_type == 'INSTR_HALT':
            self._generate_halt()
        elif instr_type == 'INSTR_PRINT':
            self._generate_print(instr[1])
        elif instr_type == 'INSTR_CALL':
            self._generate_procedure_call(instr[1], instr[2])
        elif instr_type == 'ASSIGN_CALL':
            self._generate_function_call(instr[1], instr[2], instr[3])
        elif instr_type == 'ASSIGN_TERM':
            self._generate_assignment(instr[1], instr[2])
        elif instr_type == 'LOOP_WHILE':
            self._generate_while_loop(instr[1], instr[2])
        elif instr_type == 'LOOP_DO_UNTIL':
            self._generate_do_until_loop(instr[1], instr[2])
        elif instr_type == 'BRANCH_IF':
            self._generate_if_then(instr[1], instr[2])
        elif instr_type == 'BRANCH_IF_ELSE':
            self._generate_if_else(instr[1], instr[2], instr[3])
    
    def _generate_halt(self):
        """Generate code for halt instruction"""
        self._append_code("STOP")
    
    def _generate_print(self, output):
        """Generate code for print statement"""
        if output[0] == 'OUTPUT_STRING':
            # Print string literal
            string_value = output[1]
            code = f'PRINT "{string_value}"'
            self._append_code(code)
        elif output[0] == 'OUTPUT_ATOM':
            # Print atom (variable or number)
            atom = output[1]
            atom_code = self._generate_atom(atom)
            code = f"PRINT {atom_code}"
            self._append_code(code)
    
    def _generate_assignment(self, var, term):
        """Generate code for assignment statement"""
        var_name = self._get_variable_name(var)
        term_code = self._generate_term(term)
        code = f"{var_name} = {term_code}"
        self._append_code(code)
    
    def _generate_term(self, term):
        """Generate code for TERM expression"""
        if term[0] == 'TERM_ATOM':
            return self._generate_atom(term[1])
        elif term[0] == 'TERM_UNOP':
            return self._generate_unop_term(term[1], term[2])
        elif term[0] == 'TERM_BINOP':
            return self._generate_binop_term(term[1], term[2], term[3])
        return "0"  # Default fallback
    
    def _generate_atom(self, atom):
        """Generate code for ATOM (variable or number)"""
        if atom[0] == 'ATOM_NUM':
            return str(atom[2])  # Return the number
        elif atom[0] == 'ATOM_VAR':
            var = atom[2]  # The VAR node is at index 2
            return self._get_variable_name(var)
        return "0"
    
    def _generate_unop_term(self, unop, sub_term):
        """Generate code for unary operation"""
        sub_term_code = self._generate_term(sub_term)
        
        if unop == 'NEG':
            return f"-{sub_term_code}"
        elif unop == 'NOT':
            # Handle NOT by inverting logic in conditional contexts
            # For now, return a placeholder - this will be handled in BRANCH contexts
            return f"NOT({sub_term_code})"
        
        return sub_term_code
    
    def _generate_binop_term(self, term1, binop, term2):
        """Generate code for binary operation"""
        term1_code = self._generate_term(term1)
        term2_code = self._generate_term(term2)
        
        # Map SPL operators to target language operators
        op_map = {
            'EQ': '=',
            'GT': '>',
            'PLUS': '+',
            'MINUS': '-',
            'MULT': '*',
            'DIV': '/',
            'OR': 'OR',
            'AND': 'AND'
        }
        
        operator = op_map.get(binop, binop)
        
        # Handle boolean operators with cascading technique
        if binop in ['OR', 'AND']:
            return self._generate_boolean_operation(term1_code, binop, term2_code)
        
        return f"({term1_code} {operator} {term2_code})"
    
    def _generate_boolean_operation(self, term1_code, binop, term2_code):
        """Generate code for boolean operations using cascading technique"""
        temp_var = self._get_next_temp()
        label_true = self._get_next_label()
        label_false = self._get_next_label()
        label_exit = self._get_next_label()
        
        if binop == 'OR':
            # OR: if term1 is true, jump to true; else check term2
            code = f"IF {term1_code} = 1 THEN {label_true}\n"
            code += f"IF {term2_code} = 1 THEN {label_true}\n"
            code += f"GOTO {label_false}\n"
            code += f"REM {label_true}\n"
            code += f"{temp_var} = 1\n"
            code += f"GOTO {label_exit}\n"
            code += f"REM {label_false}\n"
            code += f"{temp_var} = 0\n"
            code += f"REM {label_exit}"
            self._append_code(code)
            return temp_var
        elif binop == 'AND':
            # AND: if term1 is false, jump to false; else check term2
            code = f"IF {term1_code} = 0 THEN {label_false}\n"
            code += f"IF {term2_code} = 0 THEN {label_false}\n"
            code += f"GOTO {label_true}\n"
            code += f"REM {label_false}\n"
            code += f"{temp_var} = 0\n"
            code += f"GOTO {label_exit}\n"
            code += f"REM {label_true}\n"
            code += f"{temp_var} = 1\n"
            code += f"REM {label_exit}"
            self._append_code(code)
            return temp_var
        
        return f"({term1_code} {binop} {term2_code})"
    
    def _generate_if_then(self, condition, then_algo):
        """Generate code for if-then statement"""
        condition_code = self._generate_term(condition)
        label_then = self._get_next_label()
        label_exit = self._get_next_label()
        
        # Generate if-then structure
        code = f"IF {condition_code} = 1 THEN {label_then}\n"
        code += f"GOTO {label_exit}\n"
        code += f"REM {label_then}\n"
        
        # Generate then block code
        then_code = self._generate_algo_code(then_algo)
        if then_code:
            code += then_code + "\n"
        
        code += f"REM {label_exit}"
        self._append_code(code)
    
    def _generate_if_else(self, condition, then_algo, else_algo):
        """Generate code for if-else statement"""
        condition_code = self._generate_term(condition)
        label_then = self._get_next_label()
        label_exit = self._get_next_label()
        
        # Generate if-else structure
        code = f"IF {condition_code} = 1 THEN {label_then}\n"
        
        # Generate else block code
        else_code = self._generate_algo_code(else_algo)
        if else_code:
            code += else_code + "\n"
        
        code += f"GOTO {label_exit}\n"
        code += f"REM {label_then}\n"
        
        # Generate then block code
        then_code = self._generate_algo_code(then_algo)
        if then_code:
            code += then_code + "\n"
        
        code += f"REM {label_exit}"
        self._append_code(code)
    
    def _generate_while_loop(self, condition, loop_algo):
        """Generate code for while loop"""
        condition_code = self._generate_term(condition)
        label_loop = self._get_next_label()
        label_exit = self._get_next_label()
        
        # Generate while loop structure
        code = f"REM {label_loop}\n"
        code += f"IF {condition_code} = 0 THEN {label_exit}\n"
        
        # Generate loop body code
        loop_code = self._generate_algo_code(loop_algo)
        if loop_code:
            code += loop_code + "\n"
        
        code += f"GOTO {label_loop}\n"
        code += f"REM {label_exit}"
        self._append_code(code)
    
    def _generate_do_until_loop(self, loop_algo, condition):
        """Generate code for do-until loop"""
        condition_code = self._generate_term(condition)
        label_loop = self._get_next_label()
        label_exit = self._get_next_label()
        
        # Generate do-until loop structure
        code = f"REM {label_loop}\n"
        
        # Generate loop body code
        loop_code = self._generate_algo_code(loop_algo)
        if loop_code:
            code += loop_code + "\n"
        
        code += f"IF {condition_code} = 1 THEN {label_exit}\n"
        code += f"GOTO {label_loop}\n"
        code += f"REM {label_exit}"
        self._append_code(code)
    
    def _generate_procedure_call(self, name, input_args):
        """Generate code for procedure call"""
        name_str = self._get_function_name(name)
        args_code = self._generate_input_args(input_args)
        code = f"CALL {name_str}({args_code})"
        self._append_code(code)
    
    def _generate_function_call(self, var, name, input_args):
        """Generate code for function call with assignment"""
        var_name = self._get_variable_name(var)
        name_str = self._get_function_name(name)
        args_code = self._generate_input_args(input_args)
        code = f"{var_name} = CALL {name_str}({args_code})"
        self._append_code(code)
    
    def _generate_input_args(self, input_args):
        """Generate code for function/procedure arguments"""
        if not input_args:
            return ""
        
        args = []
        for arg in input_args:
            if arg[0] == 'ATOM_NUM':
                args.append(str(arg[2]))
            elif arg[0] == 'ATOM_VAR':
                var = arg[2]  # The VAR node is at index 2
                var_name = self._get_variable_name(var)
                args.append(var_name)
            else:
                # Handle other atom types
                atom_code = self._generate_atom(arg)
                args.append(atom_code)
        
        return ", ".join(args)
    
    def _generate_algo_code(self, algo):
        """Generate code for ALGO and return as string (for use in control structures)"""
        if not algo:
            return ""
        
        # Store current target code
        original_code = self.target_code
        self.target_code = ""
        
        # Generate code for each instruction
        for instr in algo:
            self._generate_instr(instr)
        
        # Get generated code
        generated_code = self.target_code
        
        # Restore original target code
        self.target_code = original_code
        
        return generated_code
    
    def _get_variable_name(self, var_node):
        """Extract variable name from VAR node"""
        if isinstance(var_node, tuple) and len(var_node) >= 3:
            name = var_node[2]  # VAR node structure: ('VAR', node_id, name)
            return name
        return "unknown"
    
    def _get_function_name(self, name_node):
        """Extract function name from NAME node"""
        if isinstance(name_node, tuple) and len(name_node) >= 3:
            return name_node[2]  # NAME node structure: ('NAME', node_id, name)
        return "unknown"
    
    def save_to_file(self, filename: str):
        """Save generated code to ASCII text file"""
        try:
            with open(filename, 'w', encoding='ascii') as f:
                f.write(self.target_code)
            print(f"Generated code saved to {filename}")
        except Exception as e:
            print(f"Error saving to file: {str(e)}")


def generate_intermediate_code(ast, symbol_table, output_filename: str = "output.txt") -> str:
    """
    Main function to generate intermediate code from SPL program
    
    Args:
        ast: Abstract Syntax Tree from parser
        symbol_table: Symbol table from scope analysis
        output_filename: Name of output file for generated code
        
    Returns:
        Generated intermediate code as string
    """
    generator = CodeGenerator(symbol_table)
    code = generator.generate_code(ast)
    generator.save_to_file(output_filename)
    return code


if __name__ == "__main__":
    # Test the code generator
    print("Intermediate Code Generator for SPL Compiler")
    print("This module generates intermediate code from SPL programs.")
