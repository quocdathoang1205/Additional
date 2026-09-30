@echo off
setlocal

cd /d "%~dp0"

set "PYTHON=%~dp0.venv\Scripts\python.exe"
set "SCRIPT=%~dp0Teamsnoti.py"
set "BATLOG=%~dp0Teamsnoti_launcher.log"

if /I "%~1"=="--check" (
    echo Using: "%PYTHON%"
    echo Script: "%SCRIPT%"

    if not exist "%PYTHON%" (
        echo ERROR: Python executable not found.
        exit /b 1
    )

    if not exist "%SCRIPT%" (
        echo ERROR: Python script not found.
        exit /b 1
    )

    exit /b 0
)

if not exist "%PYTHON%" (
    echo ERROR: Python executable not found:
    echo "%PYTHON%"
    pause
    exit /b 1
)

if not exist "%SCRIPT%" (
    echo ERROR: Python script not found:
    echo "%SCRIPT%"
    pause
    exit /b 1
)

echo [%date% %time%] Starting Teamsnoti.py>>"%BATLOG%"

"%PYTHON%" -u "%SCRIPT%" 2>>"%BATLOG%"
set "EXIT_CODE=%ERRORLEVEL%"

echo [%date% %time%] Python exited with code %EXIT_CODE%>>"%BATLOG%"

if not "%EXIT_CODE%"=="0" (
    echo.
    echo Teamsnoti.py stopped unexpectedly.
    echo Exit code: %EXIT_CODE%
    echo.
    echo Check these log files:
    echo "%BATLOG%"
    echo "%~dp0Teamsnoti_error.log"
    echo.
    pause
)

endlocal & exit /b %EXIT_CODE%