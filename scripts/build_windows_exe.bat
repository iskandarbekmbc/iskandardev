@echo off
setlocal

REM Windows EXE build script for Kundalik Zikrlar
REM Usage: double-click or run from cmd in repo root.

if not exist .venv (
  echo [1/5] Creating virtual environment...
  py -3 -m venv .venv
)

call .venv\Scripts\activate.bat

echo [2/5] Upgrading pip...
python -m pip install --upgrade pip

echo [3/5] Installing build dependencies...
pip install pyinstaller

echo [4/5] Building EXE with PyInstaller...
pyinstaller --noconfirm --clean --windowed --name KundalikZikrlar app.py

echo [5/5] Done.
echo EXE path: dist\KundalikZikrlar\KundalikZikrlar.exe

echo.
echo To build installer, open installer\zikr_setup.iss in Inno Setup and click Build.
endlocal
