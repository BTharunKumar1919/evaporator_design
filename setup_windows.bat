@echo off
setlocal
cd /d "%~dp0"
py -m venv .venv
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
  echo Setup failed. Check the Python installation and package installation output above.
  pause
  exit /b 1
)
echo.
echo Setup complete. Run run_app.bat to launch the app.
pause
