@echo off
cd /d "%~dp0"

if not exist "python_portable\pythonw.exe" (
    echo Box Breathing Studio is not installed yet.
    echo Please run install_app.bat first.
    pause
    exit /b 1
)

start "" "python_portable\pythonw.exe" "app.py"
