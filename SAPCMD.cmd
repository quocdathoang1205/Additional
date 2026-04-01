@ECHO OFF
CLS
ECHO 1.DVE_088_Elec
ECHO 2.DVE_068_Elec
ECHO 3.DM1_288_Marine
ECHO 4.DK2_388_Land
ECHO 5.DK2_788_Land
ECHO 6.DVT_288_Aero
ECHO 7.DVT_819_Aero
ECHO 8.S4D_100
ECHO 9.S4D_211
ECHO 0.S4D_401
ECHO A.PK2_388
ECHO B.D08_888_S4HR
ECHO C.D08_200_S4HR
ECHO D.S4S_221
ECHO E.US_PRD
ECHO.

CHOICE /C 1234567890abcde /M "Launching:"

:: Lenh duoi phai +1 cho moi option
IF ERRORLEVEL 15 GOTO USPRD
IF ERRORLEVEL 14 GOTO S4S221
IF ERRORLEVEL 13 GOTO D08200
IF ERRORLEVEL 12 GOTO D08888
IF ERRORLEVEL 11 GOTO PK2388
IF ERRORLEVEL 10 GOTO S4D401
IF ERRORLEVEL 9 GOTO S4D211
IF ERRORLEVEL 8 GOTO S4D100
IF ERRORLEVEL 7 GOTO DVT819
IF ERRORLEVEL 6 GOTO DVT288
IF ERRORLEVEL 5 GOTO DK2788
IF ERRORLEVEL 4 GOTO DK2388
IF ERRORLEVEL 3 GOTO DM1288
IF ERRORLEVEL 2 GOTO DVE068
IF ERRORLEVEL 1 GOTO DVE088

:DVE088
ECHO DVE088
cd "C:\Program Files\SAP\FrontEnd\SAPGUI"
start sapshcut.exe -system=DVE -client=088 -user=70023796 -pw=Godzilla.321
GOTO End

:DVE068
ECHO DVE068
cd "C:\Program Files\SAP\FrontEnd\SAPGUI"
start sapshcut.exe -system=DVE -client=068 -user=70023796 -pw=Godzilla.321
GOTO End

:DM1288
ECHO DM1288
cd "C:\Program Files\SAP\FrontEnd\SAPGUI"
start sapshcut.exe -system=DM1 -client=288 -user=70023796 -pw=Godzilla.321
GOTO End

:DK2388
ECHO DK2388
cd "C:\Program Files\SAP\FrontEnd\SAPGUI"
start sapshcut.exe -system=DK2 -client=388 -user=70023796 -pw=Godzilla.321
GOTO End

:DK2788
ECHO DK2788
cd "C:\Program Files\SAP\FrontEnd\SAPGUI"
start sapshcut.exe -system=DK2 -client=788 -user=70023796 -pw=Godzilla.321
GOTO End

:DVT288
ECHO DVT288
cd "C:\Program Files\SAP\FrontEnd\SAPGUI"
start sapshcut.exe -system=DVT -client=288 -user=70023796 -pw=Godzilla.321
GOTO End

:DVT819
ECHO DVT819
cd "C:\Program Files\SAP\FrontEnd\SAPGUI"
start sapshcut.exe -system=DVT -client=819 -user=70023796 -pw=Godzilla.321
GOTO End

:S4D100
ECHO S4D100
cd "C:\Program Files\SAP\FrontEnd\SAPGUI"
start sapshcut.exe -group=S4D -system=S4D -client=100 -user=70023796 -pw=Godzilla.321321
GOTO End

:S4D211
ECHO S4D211
cd "C:\Program Files\SAP\FrontEnd\SAPGUI"
start sapshcut.exe -group=S4D -system=S4D -client=211 -user=70023796 -pw=Godzilla.123456
GOTO End

:S4D401
ECHO S4D401
cd "C:\Program Files\SAP\FrontEnd\SAPGUI"
start sapshcut.exe -group=S4D -system=S4D -client=401 -user=70023796 -pw=Godzilla.321321
GOTO End

:PK2388
ECHO PK2388
cd "C:\Program Files\SAP\FrontEnd\SAPGUI"
start sapshcut.exe -system=PK2 -client=388 -user=88900203 -pw=FICOteam***1
GOTO End

:D08888
ECHO D08888
cd "C:\Program Files\SAP\FrontEnd\SAPGUI"
start sapshcut.exe -system=D08 -client=888 -user=70023796 -pw=Godzilla.123
GOTO End

:D08200
ECHO D08200
cd "C:\Program Files\SAP\FrontEnd\SAPGUI"
start sapshcut.exe -system=D08 -client=200 -user=70023796 -pw=Godzilla.123
GOTO End

:S4S221
ECHO S4S221
cd "C:\Program Files\SAP\FrontEnd\SAPGUI"
start sapshcut.exe -system=S4S -client=221 -user=70023796 -pw=Godzilla.321321
GOTO End

:USPRD
ECHO USPRD
cd "C:\Program Files\SAP\FrontEnd\SAPGUI"
start sapshcut.exe -system=PRD -client=288 -user=70023796 -pw=Godzilla.1205 -sysname="USA PRD US SAA MAE"
GOTO End

:End