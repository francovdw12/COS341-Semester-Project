# COS341-Semester-Project

## EXPLANATION
* ```lexer.py``` - The lexer.
* ```parser.py``` - The parser.
* ```semantics.py``` - Scoping and basic type checking.
* ```typespec.py``` - Proper type checking.
* ```codegen.py``` - Intermediate code generation (but this one had an issue with CALL statements).
* ```codegen_inline.py``` - Intermediate code generation (but with no problems as far as I know).
* ```basicify.py``` - The conversion from intermediate code to BASIC code.
* ```input.spl``` - The SPL code you want to compile (using the commands below)


## HOW TO RUN:

(Run basicify.py with Python. input.spl is the student language you want to compile. program.bas is the output (BASIC code))
```python basicify.py input.spl program.bas```

(This one you need to pip install the pcbasic thing - this will take the program.bas BASIC code and run it and put the output in program.out.txt)
```pcbasic --run=program.bas --output=program.out.txt --quit```


## NOTES
* Not sure if we need to remove all test code for final submission... Probably?
* We need to check out the code and fix stuff like random test code at the bottom of files, unnecessary comments, stuff like that
