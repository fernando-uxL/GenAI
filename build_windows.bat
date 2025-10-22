@echo off
setlocal

REM Create and activate a venv to keep things clean (optional but recommended)
python -m venv .venv
call .venv\Scripts\activate

REM Upgrade pip and install requirements + pyinstaller
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

REM Build single-file EXE with icon, no console window
pyinstaller --onefile --windowed --icon=icon.ico AI_Summarizer.py

echo.
echo Build complete. Find your EXE in the "dist" folder.
echo.

pause
