"""
SPL Compiler - Main Driver
COS341 Semester Project 2025

This is the main entry point for the SPL compiler.
It reads SPL source code from .txt files and runs all compilation phases:
1. Lexer (Tokenization)
2. Parser (Syntax Analysis)
3. Scope Analyzer (Semantic Analysis)
4. Type Checker (Type Analysis)
5. Code Generator (Intermediate Code Generation)
6. Inliner (CALL Instruction Inlining)

Usage:
    python compiler.py <input_file.txt> [options]
    
Options:
    --output <file>         Specify output file for intermediate code (default: intermediate_code.txt)
    --inlined <file>        Specify output file for inlined code (default: inlined_code.txt)
    --verbose              Show detailed output from each phase
    --quiet                Show minimal output (errors only)
    --help                 Show this help message

Examples:
    python compiler.py program.txt
    python compiler.py program.txt --output my_output.txt --verbose
    python compiler.py program.txt --quiet
"""

import sys
import os
from pathlib import Path

# Import all compiler phases
from lexer import SPLLexer
from parser import parse_spl
from semantic_analyzer import ScopeAnalyzer, print_semantic_errors
from type_checker import check_spl_types, print_type_errors
from code_generator import generate_intermediate_code
from inliner import inline_intermediate_code


class SPLCompiler:
    """Main SPL Compiler class that orchestrates all compilation phases."""
    
    def __init__(self, verbose=False, quiet=False):
        """
        Initialize the compiler.
        
        Args:
            verbose (bool): Enable detailed output
            quiet (bool): Suppress all non-error output
        """
        self.verbose = verbose
        self.quiet = quiet
        self.errors = []
        
    def log(self, message, force=False):
        """Print message unless in quiet mode."""
        if force or not self.quiet:
            print(message)
    
    def log_verbose(self, message):
        """Print message only in verbose mode."""
        if self.verbose:
            print(message)
    
    def read_source_file(self, filename):
        """
        Read SPL source code from a .txt file.
        
        Args:
            filename (str): Path to the source file
            
        Returns:
            str: Source code content, or None if reading fails
        """
        try:
            # Check if file exists
            if not os.path.exists(filename):
                self.log(f"ERROR: File not found: {filename}", force=True)
                return None
            
            # Check file extension
            if not filename.endswith('.txt'):
                self.log(f"WARNING: Expected .txt file, got: {filename}")
            
            # Read file with proper encoding
            with open(filename, 'r', encoding='utf-8') as f:
                source_code = f.read()
            
            self.log_verbose(f"Successfully read {len(source_code)} characters from {filename}")
            return source_code
            
        except UnicodeDecodeError:
            # Try with different encoding if UTF-8 fails
            try:
                with open(filename, 'r', encoding='latin-1') as f:
                    source_code = f.read()
                self.log(f"WARNING: File read with latin-1 encoding instead of UTF-8")
                return source_code
            except Exception as e:
                self.log(f"ERROR: Failed to read file: {str(e)}", force=True)
                return None
                
        except Exception as e:
            self.log(f"ERROR: Failed to read file: {str(e)}", force=True)
            return None
    
    def compile(self, source_code, output_file="intermediate_code.txt", inlined_file="inlined_code.txt"):
        """
        Compile SPL source code through all six phases.
        
        Args:
            source_code (str): SPL source code
            output_file (str): Output file for intermediate code
            inlined_file (str): Output file for inlined code
            
        Returns:
            bool: True if compilation succeeds, False otherwise
        """
        if not source_code or source_code.strip() == "":
            self.log("ERROR: Empty source code", force=True)
            return False
        
        self.log("\n" + "=" * 80)
        self.log("SPL COMPILER - Six Phase Compilation")
        self.log("=" * 80)
        
        # ====================================================================
        # PHASE 1: LEXER (Tokenization)
        # ====================================================================
        self.log("\n[PHASE 1] LEXER - Tokenization")
        self.log("-" * 40)
        
        try:
            lexer = SPLLexer()
            tokens = list(lexer.tokenize(source_code))
            
            if not tokens:
                self.log("ERROR: No tokens generated - source may be empty or invalid", force=True)
                return False
            
            self.log(f"✓ Tokenization successful: {len(tokens)} tokens generated")
            self.log_verbose(f"  Token types: {set(t.type for t in tokens)}")
            
        except Exception as e:
            self.log(f"✗ LEXER ERROR: {str(e)}", force=True)
            return False
        
        # ====================================================================
        # PHASE 2: PARSER (Syntax Analysis)
        # ====================================================================
        self.log("\n[PHASE 2] PARSER - Syntax Analysis")
        self.log("-" * 40)
        
        try:
            parse_tree = parse_spl(source_code)
            
            if not parse_tree:
                self.log("✗ PARSER ERROR: Parsing failed - check syntax", force=True)
                return False
            
            self.log("✓ Parsing successful: Abstract Syntax Tree (AST) created")
            
            # Display AST structure info
            if parse_tree[0] == 'SPL_PROG':
                global_vars = len(parse_tree[2]) if parse_tree[2] else 0
                procedures = len(parse_tree[3]) if parse_tree[3] else 0
                functions = len(parse_tree[4]) if parse_tree[4] else 0
                
                self.log(f"  Program structure:")
                self.log(f"    - Global variables: {global_vars}")
                self.log(f"    - Procedures: {procedures}")
                self.log(f"    - Functions: {functions}")
                self.log_verbose(f"    - Root node ID: {parse_tree[1]}")
                
        except Exception as e:
            self.log(f"✗ PARSER ERROR: {str(e)}", force=True)
            return False
        
        # ====================================================================
        # PHASE 3: SCOPE ANALYZER (Semantic Analysis)
        # ====================================================================
        self.log("\n[PHASE 3] SCOPE ANALYZER - Semantic Analysis")
        self.log("-" * 40)
        
        try:
            analyzer = ScopeAnalyzer()
            success, errors = analyzer.analyze(parse_tree)
            
            if not success:
                self.log("✗ SEMANTIC ERRORS DETECTED:", force=True)
                print_semantic_errors(errors)
                return False
            
            self.log("✓ Semantic analysis passed")
            
            # Get symbol table size safely
            try:
                if hasattr(analyzer.symbol_table, '__len__'):
                    table_size = len(analyzer.symbol_table)
                elif hasattr(analyzer.symbol_table, 'get_all_symbols'):
                    table_size = len(analyzer.symbol_table.get_all_symbols())
                else:
                    table_size = "N/A"
                self.log(f"  Symbol table entries: {table_size}")
            except:
                pass
            
            if errors:
                self.log("  Warnings:")
                print_semantic_errors(errors)
                
        except Exception as e:
            self.log(f"✗ SEMANTIC ANALYZER ERROR: {str(e)}", force=True)
            return False
        
        # ====================================================================
        # PHASE 4: TYPE CHECKER (Type Analysis)
        # ====================================================================
        self.log("\n[PHASE 4] TYPE CHECKER - Type Analysis")
        self.log("-" * 40)
        
        try:
            type_success, type_errors = check_spl_types(parse_tree, analyzer.symbol_table)
            
            if not type_success:
                self.log("✗ TYPE ERRORS DETECTED:", force=True)
                print_type_errors(type_errors)
                return False
            
            self.log("✓ Type analysis passed")
            
            if type_errors:
                self.log("  Type warnings:")
                print_type_errors(type_errors)
                
        except Exception as e:
            self.log(f"✗ TYPE CHECKER ERROR: {str(e)}", force=True)
            return False
        
        # ====================================================================
        # PHASE 5: CODE GENERATOR (Intermediate Code Generation)
        # ====================================================================
        self.log("\n[PHASE 5] CODE GENERATOR - Intermediate Code Generation")
        self.log("-" * 40)
        
        try:
            intermediate_code = generate_intermediate_code(parse_tree, analyzer.symbol_table, output_file)
            
            if not intermediate_code:
                self.log("✗ CODE GENERATION ERROR: No code generated", force=True)
                return False
            
            self.log(f"✓ Intermediate code generated successfully")
            self.log(f"  Output file: {output_file}")
            self.log(f"  Lines of code: {len(intermediate_code.strip().split(chr(10)))}")
            
            if self.verbose:
                self.log("\n  Generated code preview:")
                self.log("  " + "-" * 40)
                preview_lines = intermediate_code.strip().split('\n')[:15]
                for line in preview_lines:
                    self.log(f"  {line}")
                if len(intermediate_code.strip().split('\n')) > 15:
                    self.log(f"  ... ({len(intermediate_code.strip().split(chr(10))) - 15} more lines)")
                self.log("  " + "-" * 40)
                
        except Exception as e:
            self.log(f"✗ CODE GENERATOR ERROR: {str(e)}", force=True)
            return False
        
        # ====================================================================
        # PHASE 6: INLINER (CALL Instruction Inlining)
        # ====================================================================
        self.log("\n[PHASE 6] INLINER - CALL Instruction Replacement")
        self.log("-" * 40)
        
        try:
            inlined_code = inline_intermediate_code(parse_tree, analyzer.symbol_table, 
                                                   intermediate_code, inlined_file)
            
            if not inlined_code:
                self.log("✗ INLINING ERROR: Failed to inline code", force=True)
                return False
            
            self.log(f"✓ Inlining completed successfully")
            self.log(f"  Output file: {inlined_file}")
            self.log(f"  Lines of inlined code: {len(inlined_code.strip().split(chr(10)))}")
            
            if self.verbose:
                self.log("\n  Inlined code preview:")
                self.log("  " + "-" * 40)
                preview_lines = inlined_code.strip().split('\n')[:15]
                for line in preview_lines:
                    self.log(f"  {line}")
                if len(inlined_code.strip().split('\n')) > 15:
                    self.log(f"  ... ({len(inlined_code.strip().split(chr(10))) - 15} more lines)")
                self.log("  " + "-" * 40)
                
        except Exception as e:
            self.log(f"✗ INLINER ERROR: {str(e)}", force=True)
            return False
        
        # ====================================================================
        # COMPILATION SUMMARY
        # ====================================================================
        self.log("\n" + "=" * 80)
        self.log("✓✓✓ COMPILATION SUCCESSFUL ✓✓✓")
        self.log("=" * 80)
        self.log("All six phases completed successfully:")
        self.log("  [1] Lexer: Tokenization ✓")
        self.log("  [2] Parser: Syntax Analysis ✓")
        self.log("  [3] Scope Analyzer: Semantic Analysis ✓")
        self.log("  [4] Type Checker: Type Analysis ✓")
        self.log("  [5] Code Generator: Intermediate Code ✓")
        self.log("  [6] Inliner: CALL Instruction Replacement ✓")
        self.log("\nOutput files:")
        self.log(f"  - Intermediate code: {output_file}")
        self.log(f"  - Inlined code: {inlined_file}")
        self.log("=" * 80)
        
        return True
    
    def compile_file(self, input_file, output_file="intermediate_code.txt", 
                    inlined_file="inlined_code.txt"):
        """
        Compile an SPL source file.
        
        Args:
            input_file (str): Path to input .txt file
            output_file (str): Output file for intermediate code
            inlined_file (str): Output file for inlined code
            
        Returns:
            bool: True if compilation succeeds, False otherwise
        """
        self.log(f"\nReading source file: {input_file}")
        
        # Read source code from file
        source_code = self.read_source_file(input_file)
        
        if source_code is None:
            return False
        
        # Compile the source code
        return self.compile(source_code, output_file, inlined_file)


def print_help():
    """Print help message."""
    print(__doc__)


def main():
    """Main entry point for the compiler."""
    
    # Parse command-line arguments
    if len(sys.argv) < 2 or '--help' in sys.argv or '-h' in sys.argv:
        print_help()
        return 0
    
    input_file = sys.argv[1]
    output_file = "intermediate_code.txt"
    inlined_file = "inlined_code.txt"
    verbose = False
    quiet = False
    
    # Process optional arguments
    i = 2
    while i < len(sys.argv):
        arg = sys.argv[i]
        
        if arg == '--output' and i + 1 < len(sys.argv):
            output_file = sys.argv[i + 1]
            i += 2
        elif arg == '--inlined' and i + 1 < len(sys.argv):
            inlined_file = sys.argv[i + 1]
            i += 2
        elif arg == '--verbose':
            verbose = True
            i += 1
        elif arg == '--quiet':
            quiet = True
            i += 1
        else:
            print(f"WARNING: Unknown argument: {arg}")
            i += 1
    
    # Create compiler instance
    compiler = SPLCompiler(verbose=verbose, quiet=quiet)
    
    # Compile the file
    success = compiler.compile_file(input_file, output_file, inlined_file)
    
    # Return appropriate exit code
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
