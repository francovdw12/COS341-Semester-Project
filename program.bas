10 counter = 0
20 maxvalue = 100
30 num1 = 15
40 num2 = 25
50 num3 = 35
60 testvar1 = 10
70 testvar2 = 20
80 testvar3 = 30
90 CALL calculateandstore ( num1 num2 num3 )
100 CALL findandstoremax ( num1 num2 )
110 CALL multiplyandstore ( num1 num2 )
120 CALL complexcalculation ( testvar1 testvar2 testvar3 )
130 CALL nestedprocedure ( num1 num2 )
140 funcresult1 = CALL calculatesum ( num1 num2 num3 )
150 funcresult2 = CALL multiply ( num1 num2 )
160 funcresult3 = CALL factorial ( 5 )
170 funcresult4 = CALL power ( 2 3 )
180 PRINT "funcsum"
190 PRINT funcresult1
200 PRINT "funcmult"
210 PRINT funcresult2
220 PRINT "funcfact"
230 PRINT funcresult3
240 PRINT "funcpower"
250 PRINT funcresult4
260 loopcount = 0
270 REM W0001
280 IF loopcount > 0 THEN 300
290 GOTO 340
300 REM WB0002
310 CALL incrementcounter (  )
320 loopcount = (loopcount - 1)
330 GOTO 270
340 REM WX0003
350 result = (sumresult * maxnum)
360 PRINT "final"
370 PRINT result
380 CALL resetcounter (  )
390 STOP
