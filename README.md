# COS341-Semester-Project

## EXPLANATION
* ```lexer.py``` - The lexer
* ```parser.py``` - The parser
* ```semantics.py``` - Scoping and basic type checking
* ```typespec.py``` - Proper type checking
* ```codegen_inline.py``` - Intermediate code generation (with function inlining)
* ```basicify.py``` - The conversion from intermediate code to BASIC code.

* ```input.txt``` - The SPL code you want to compile (using the commands below)
* ```program.bas``` - Generated BASIC code output from basicify.py
* ```program.out.txt``` - Final execution output from running the BASIC program

* ```/tests``` - Test suite containing all test files for the compiler components 


## HOW TO RUN:

### Prerequisites
1. Install Python 3.x
2. Install pcbasic: `pip install pcbasic` (we are using pcbasic as our emulator)

### Compilation Steps

**Step 1: Compile SPL to BASIC**
```bash
python basicify.py input.txt program.bas
```
This converts your SPL source code (`input.txt`) into BASIC code (`program.bas`).

**Step 2: Run the BASIC program**
```bash
pcbasic --run=program.bas --output=program.out.txt --quit
```
This executes the generated BASIC code and saves the output to `program.out.txt`.




