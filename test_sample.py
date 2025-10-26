"""
Test a sample SPL program through all six compiler phases:
1. Lexer (tokenization)
2. Parser (syntax analysis) 
3. Scope Analyzer (semantic analysis)
4. Type Checker (type analysis)
5. Code Generator (intermediate code generation)
6. Inliner (CALL instruction inlining)
"""

from lexer import SPLLexer
from parser import parse_spl
from semantic_analyzer import analyze_spl_semantics, print_semantic_errors, ScopeAnalyzer
from type_checker import check_spl_types, print_type_errors
from code_generator import generate_intermediate_code
from inliner import inline_intermediate_code

def test_sample_program():
    """Test a sample SPL program through all six phases."""
    
    # Comprehensive SPL program with multiple procedures and variables
    sample_code =  """
    glob { 
        counter 
        maxvalue 
        result 
        sumresult 
        maxnum 
        multresult 
        temp1 
        temp2 
        temp3 
        
    }
    proc {
        displaycounter ( ) {
            local { }
            print counter;
            print "counter"
        }
        
        incrementcounter ( ) {
            local { }
            counter = ( counter plus 1 );
            displaycounter ( )
        }
        
        resetcounter ( ) {
            local { }
            counter = 0;
            print "reset"
        }
        
        calculateandstore ( a b c ) {
            local { 
                temp 
                sum 
            }
            temp = ( a plus b );
            sum = ( temp plus c );
            sumresult = sum;
            print "calculated";
            print sumresult
        }
        
        findandstoremax ( x y ) {
            local { }
            if ( x > y ) {
                maxnum = x;
                print "maxx";
                print x
            } else {
                maxnum = y;
                print "maxy";
                print y
            }
        }
        
        multiplyandstore ( a b ) {
            local { }
            multresult = ( a mult b );
            print "mult";
            print multresult
        }
        
        complexcalculation ( x y z ) {
            local { 
                step1 
                step2 
                step3 
            }
            step1 = ( x plus y );
            step2 = ( step1 mult z );
            step3 = ( step2 minus x );
            temp1 = step1;
            temp2 = step2;
            temp3 = step3;
            print "step1";
            print step1;
            print "step2";
            print step2;
            print "step3";
            print step3
        }
        
        nestedprocedure ( a b ) {
            local { 
                inner1 
                inner2 
            }
            inner1 = ( a plus b );
            inner2 = ( inner1 mult 2 );
            print "inner1";
            print inner1;
            print "inner2";
            print inner2;
            if ( inner1 > inner2 ) {
                print "inner1bigger";
                print inner1
            } else {
                print "inner2bigger";
                print inner2
            }
        }
    }
    func {
        calculatesum ( a b c ) {
            local { 
                temp 
                sum 
            }
            temp = ( a plus b );
            sum = ( temp plus c );
            return sum
        }
        
        multiply ( a b ) {
            local { result }
            result = ( a mult b );
            return result
        }

        factorial ( n ) {
            local { 
                fact 
                i 
            }
            fact = 1;
            i = n;
            while ( i > 0 ) {
                fact = ( fact mult i );
                i = ( i minus 1 )
            };
            return fact
        }
        
        power ( base exp ) {
            local { 
                result 
                count 
            }
            result = 1;
            count = 0;
            while ( count > 0 ) {
                result = ( result mult base );
                count = ( count minus 1 )
            };
            return result
        }
        
    }
    main {
        var { 
            num1 
            num2 
            num3 
            loopcount 
            testvar1 
            testvar2 
            testvar3 
            funcresult1 
            funcresult2 
            funcresult3 
            funcresult4 
        }
        counter = 0;
        maxvalue = 100;
        num1 = 15;
        num2 = 25;
        num3 = 35;
        testvar1 = 10;
        testvar2 = 20;
        testvar3 = 30;
        calculateandstore ( num1 num2 num3 );
        findandstoremax ( num1 num2 );
        multiplyandstore ( num1 num2 );
        complexcalculation ( testvar1 testvar2 testvar3 );
        nestedprocedure ( num1 num2 );
        funcresult1 = calculatesum ( num1 num2 num3 );
        funcresult2 = multiply ( num1 num2 );
        funcresult3 = factorial ( 5 );
        funcresult4 = power ( 2 3 );
        print "funcsum";
        print funcresult1;
        print "funcmult";
        print funcresult2;
        print "funcfact";
        print funcresult3;
        print "funcpower";
        print funcresult4;
        loopcount = 0;
        while ( loopcount > 0 ) {
            incrementcounter ( );
            loopcount = ( loopcount minus 1 )
        };
        result = ( sumresult mult maxnum );
        print "final";
        print result;
        resetcounter ( );
        halt
    }
    """

    # # TEST 1
    # #===================================================================
    # sample_code = """
    # glob { total }
    # proc { }
    # func {
    #     add ( x y ) {
    #         local { result }
    #         result = ( x plus y );
    #         return result
    #     }
    # }
    # main {
    #     var { a b }
    #     a = 10;
    #     b = 20;
    #     total = add ( a b );
    #     print total;
    #     halt
    # }

    # """

    # # TEST 2
    # #===================================================================
    # sample_code = """
    # glob {
    # }

    # proc {
    # }

    # func {
    #     testfunc(a) {
    #         local { }
    #         return a
    #     }
    # }

    # main {
    #     var { x y }
    #     x = 5;
    #     y = testfunc(x);
    #     print y;
    #     halt
    # }
    # """

# #     # TEST 3
# #     #===================================================================
#     sample_code = """
#     glob { total }
#     proc { }
#     func {
#         add ( x y ) {
#             local { result }
#             result = ( x plus y );
#             return result
#         }
#     }
#     main {
#         var { a b }
#         a = 10;
#         b = 20;
#         total = add ( a b );
#         print total;
#         halt
#     }
#     """

    # TEST 4
    #===================================================================
    sample_code = """
    glob { maxval }
    proc { }
    func {
        findmaximum ( x y ) {
            local { result }
            if ( x > y ) {
                result = x
            } else {
                result = y
            };
            return result
        }
    }

    main {
        var { a b }
        a = 7;
        b = 12;
        maxval = findmaximum ( a b );
        print maxval;
        halt
    }
    """
    
    print("=" * 80)
    print("SPL COMPILER - SIX PHASE TEST")
    print("=" * 80)
    print("\nSample Program:")
    print(sample_code)
    print("=" * 80)
    
    # Phase 1: Lexer (Tokenization)
    print("\nPHASE 1: LEXER (Tokenization)")
    print("-" * 40)
    lexer = SPLLexer()
    tokens = list(lexer.tokenize(sample_code))
    print(f"OK: Generated {len(tokens)} tokens")
    print("First 10 tokens:")
    for i, token in enumerate(tokens[:10]):
        print(f"  {i+1:2d}. {token.type:12s} = '{token.value}'")
    if len(tokens) > 10:
        print(f"  ... and {len(tokens) - 10} more tokens")
    
    # Phase 2: Parser (Syntax Analysis)
    print("\nPHASE 2: PARSER (Syntax Analysis)")
    print("-" * 40)
    parse_tree = parse_spl(sample_code)
    if parse_tree:
        print("OK: Parsing successful!")
        print("Parse tree structure:")
        print(f"  Root: {parse_tree[0]}")
        print(f"  Global variables: {len(parse_tree[2])} variables")
        print(f"  Procedures: {len(parse_tree[3])} procedures")
        print(f"  Functions: {len(parse_tree[4])} functions")
        print(f"  Main program: {len(parse_tree[5][2])} local variables, {len(parse_tree[5][3])} instructions")
    else:
        print("FAIL: Parsing failed!")
        return False
    
    # Phase 3: Scope Analyzer (Semantic Analysis)
    print("\nPHASE 3: SCOPE ANALYZER (Semantic Analysis)")
    print("-" * 40)
    
    # Create scope analyzer and analyze
    analyzer = ScopeAnalyzer()
    success, errors = analyzer.analyze(parse_tree)
    
    if success:
        print("OK: Scope analysis passed!")
        print_semantic_errors(errors)
    else:
        print("FAIL: Scope analysis failed!")
        print_semantic_errors(errors)
        return False
    
    # Phase 4: Type Checker (Type Analysis)
    print("\nPHASE 4: TYPE CHECKER (Type Analysis)")
    print("-" * 40)
    
    # Check types using the symbol table from scope analysis
    type_success, type_errors = check_spl_types(parse_tree, analyzer.symbol_table)
    
    if type_success:
        print("OK: Type analysis passed!")
        print_type_errors(type_errors)
    else:
        print("FAIL: Type analysis failed!")
        print_type_errors(type_errors)
        return False
    
    # Phase 5: Code Generator (Intermediate Code Generation)
    print("\nPHASE 5: CODE GENERATOR (Intermediate Code Generation)")
    print("-" * 40)
    
    try:
        intermediate_code = generate_intermediate_code(parse_tree, analyzer.symbol_table, "sample_intermediate.txt")
        
        if intermediate_code:
            print("OK: Code generation successful!")
            print("\nGenerated Intermediate Code (with CALL instructions):")
            print("-" * 50)
            print(intermediate_code)
            print("-" * 50)
            print(f"Intermediate code saved to: sample_intermediate.txt")
        else:
            print("FAIL: Code generation failed!")
            return False
            
    except Exception as e:
        print(f"FAIL: Code generation error: {str(e)}")
        return False
    
    # Phase 6: Inliner (Replace CALL instructions with inlined code)
    print("\nPHASE 6: INLINER (Replace CALL with inlined code)")
    print("-" * 40)
    
    try:
        inlined_code = inline_intermediate_code(parse_tree, analyzer.symbol_table, intermediate_code, "sample_inlined.txt")
        
        if inlined_code:
            print("OK: Inlining successful!")
            print("\nInlined Code (CALL instructions replaced):")
            print("-" * 50)
            print(inlined_code)
            print("-" * 50)
            print(f"Inlined code saved to: sample_inlined.txt")
        else:
            print("FAIL: Inlining failed!")
            return False
            
    except Exception as e:
        print(f"FAIL: Inlining error: {str(e)}")
        return False
    
    # Display Symbol Table
    print("\nSYMBOL TABLE:")
    print("-" * 40)
    print("Scopes and Symbols:")
    for scope_id, scope in analyzer.symbol_table.scopes.items():
        print(f"\nScope: {scope_id} ({scope.scope_type.value})")
        if scope.parent_scope_id:
            print(f"  Parent: {scope.parent_scope_id}")
        if scope.symbols:
            print("  Symbols:")
            for name, symbol in scope.symbols.items():
                print(f"    {name}: {symbol.symbol_type.value} (node_id: {symbol.node_id})")
        else:
            print("  (No symbols)")
    
    # Display Symbol Table Entries by Node ID
    print(f"\nSymbol Table Entries (by Node ID):")
    print("-" * 40)
    for node_id, entry in analyzer.symbol_table.entries.items():
        print(f"Node {node_id}: {entry.name} ({entry.symbol_type.value}) in {entry.scope_id}")
    
    # Summary
    print("\n" + "=" * 80)
    print("SIX PHASE COMPILER SUMMARY")
    print("=" * 80)
    print("OK: Phase 1 (Lexer): Tokenization successful")
    print("OK: Phase 2 (Parser): Syntax analysis successful") 
    print("OK: Phase 3 (Scope Analyzer): Semantic analysis successful")
    print("OK: Phase 4 (Type Checker): Type analysis successful")
    print("OK: Phase 5 (Code Generator): Intermediate code generation successful")
    print("OK: Phase 6 (Inliner): CALL instruction inlining successful")
    print("\nSUCCESS: ALL SIX PHASES COMPLETED SUCCESSFULLY!")
    print("Your SPL program has been fully compiled with inlined code.")
    print("All CALL instructions have been replaced with actual function/procedure code!")
    print("=" * 80)
    
    return True

if __name__ == "__main__":
    test_sample_program()