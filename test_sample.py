"""
Test a sample SPL program through all three compiler phases:
1. Lexer (tokenization)
2. Parser (syntax analysis) 
3. Scope Analyzer (semantic analysis)
"""

from lexer import SPLLexer
from parser import parse_spl
from semantic_analyzer import analyze_spl_semantics, print_semantic_errors, ScopeAnalyzer

def test_sample_program():
    """Test a sample SPL program through all three phases."""
    
    # Comprehensive SPL program with multiple procedures and variables
    sample_code = """
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
            i = 1;
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
    
    print("=" * 80)
    print("SPL COMPILER - THREE PHASE TEST")
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
    print("SUMMARY")
    print("=" * 80)
    print("OK: Phase 1 (Lexer): Tokenization successful")
    print("OK: Phase 2 (Parser): Syntax analysis successful") 
    print("OK: Phase 3 (Scope Analyzer): Semantic analysis successful")
    print("\nSUCCESS: ALL THREE PHASES COMPLETED SUCCESSFULLY!")
    print("Your SPL program is syntactically and semantically correct.")
    print("=" * 80)
    
    return True

if __name__ == "__main__":
    test_sample_program()