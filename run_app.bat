@echo off
setlocal
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
  echo Virtual environment not found. First run setup_windows.bat.
  pause
  exit /b 1
)
call .venv\Scripts\activate.bat
python -m streamlit run app.py
