@echo off
REM Aktivasi venv tanpa PowerShell script (hindari error ExecutionPolicy)
cd /d "%~dp0"
call venv\Scripts\activate.bat
cmd /k
