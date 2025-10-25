10 counter = 0
20 maxvalue = 100
30 num1 = 15
40 num2 = 25
50 num3 = 35
60 testvar1 = 10
70 testvar2 = 20
80 testvar3 = 30
90 P1a = num1
100 P2b = num2
110 P3c = num3
120 L4temp = (P1a + P2b)
130 L5sum = (L4temp + P3c)
140 sumresult = L5sum
150 PRINT "calculated"
160 PRINT sumresult
170 P6x = num1
180 P7y = num2
190 IF P6x > P7y THEN 240
200 maxnum = P7y
210 PRINT "maxy"
220 PRINT P7y
230 GOTO 280
240 REM T0001
250 maxnum = P6x
260 PRINT "maxx"
270 PRINT P6x
280 REM X0002
290 P8a = num1
300 P9b = num2
310 multresult = (P8a * P9b)
320 PRINT "mult"
330 PRINT multresult
340 P10x = testvar1
350 P11y = testvar2
360 P12z = testvar3
370 L13step1 = (P10x + P11y)
380 L14step2 = (L13step1 * P12z)
390 L15step3 = (L14step2 - P10x)
400 temp1 = L13step1
410 temp2 = L14step2
420 temp3 = L15step3
430 PRINT "step1"
440 PRINT L13step1
450 PRINT "step2"
460 PRINT L14step2
470 PRINT "step3"
480 PRINT L15step3
490 P16a = num1
500 P17b = num2
510 L18inner1 = (P16a + P17b)
520 L19inner2 = (L18inner1 * 2)
530 PRINT "inner1"
540 PRINT L18inner1
550 PRINT "inner2"
560 PRINT L19inner2
570 IF L18inner1 > L19inner2 THEN 610
580 PRINT "inner2bigger"
590 PRINT L19inner2
600 GOTO 640
610 REM T0003
620 PRINT "inner1bigger"
630 PRINT L18inner1
640 REM X0004
650 P20a = num1
660 P21b = num2
670 P22c = num3
680 L23temp = (P20a + P21b)
690 L24sum = (L23temp + P22c)
700 funcresult1 = L24sum
710 P25a = num1
720 P26b = num2
730 L27result = (P25a * P26b)
740 funcresult2 = L27result
750 P28n = 5
760 L29fact = 1
770 L30i = P28n
780 REM W0005
790 IF L30i > 0 THEN 810
800 GOTO 850
810 REM WB0006
820 L29fact = (L29fact * L30i)
830 L30i = (L30i - 1)
840 GOTO 780
850 REM WX0007
860 funcresult3 = L29fact
870 P31base = 2
880 P32exp = 3
890 L33result = 1
900 L34count = P32exp
910 REM W0008
920 IF L34count > 0 THEN 940
930 GOTO 980
940 REM WB0009
950 L33result = (L33result * P31base)
960 L34count = (L34count - 1)
970 GOTO 910
980 REM WX0010
990 funcresult4 = L33result
1000 PRINT "funcsum"
1010 PRINT funcresult1
1020 PRINT "funcmult"
1030 PRINT funcresult2
1040 PRINT "funcfact"
1050 PRINT funcresult3
1060 PRINT "funcpower"
1070 PRINT funcresult4
1080 loopcount = 0
1090 REM W0011
1100 IF loopcount > 0 THEN 1120
1110 GOTO 1180
1120 REM WB0012
1130 counter = (counter + 1)
1140 PRINT counter
1150 PRINT "counter"
1160 loopcount = (loopcount - 1)
1170 GOTO 1090
1180 REM WX0013
1190 result = (sumresult * maxnum)
1200 PRINT "final"
1210 PRINT result
1220 counter = 0
1230 PRINT "reset"
1240 STOP
