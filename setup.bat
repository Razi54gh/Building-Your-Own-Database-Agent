@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ============================================
echo  SETUP - Database Agent (Multi Provider)
echo ============================================

if not exist "venv\Scripts\python.exe" (
    echo [1/4] Membuat venv...
    python -m venv venv
) else (
    echo [1/4] venv sudah ada.
)

echo [2/4] Install package...
venv\Scripts\python.exe -m pip install --upgrade pip -q
venv\Scripts\python.exe -m pip install -r requirements.txt -q

echo [3/4] Siapkan data...
venv\Scripts\python.exe setup_data.py

if not exist ".env" (
    copy .env.example .env >nul
    echo File .env dibuat. Default provider: Ollama
)

echo [4/4] Verifikasi...
venv\Scripts\python.exe verify_setup.py

echo.
echo Provider default: Ollama (gratis)
echo 1. Install Ollama: https://ollama.com
echo 2. ollama pull llama3.1:8b
echo 3. Buka VS Code, pilih kernel venv\Scripts\python.exe
pause
