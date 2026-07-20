@echo off
setlocal

cd /d "%~dp0"

if /I "%~1"=="--check" (
    echo Using: "%~dp0.venv\Scripts\python.exe"
    echo Script: "%~dp0Teamsnoti.py"
    exit /b 0
)

"%~dp0.venv\Scripts\python.exe" "%~dp0Teamsnoti.py"

endlocal