@echo off
title PDF Forensic Sanitizer - Auto Builder
color 0A

echo.
echo  ============================================================
echo   PDF FORENSIC SANITIZER - Automatic Windows EXE Builder
echo  ============================================================
echo.
echo  This script will:
echo    1. Check for Python installation
echo    2. Install PyInstaller
echo    3. Build the EXE file
echo.
echo  Press any key to start...
pause >nul

REM Check if Python is installed
echo.
echo [Step 1/4] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo  ERROR: Python is not installed!
    echo.
    echo  Please download and install Python from:
    echo  https://www.python.org/downloads/
    echo.
    echo  IMPORTANT: During installation, check the box:
    echo  [x] "Add Python to PATH"
    echo.
    pause
    exit /b 1
)
python --version
echo  [OK] Python found!

REM Install PyInstaller
echo.
echo [Step 2/4] Installing PyInstaller...
pip install pyinstaller --quiet --disable-pip-version-check
if errorlevel 1 (
    echo  Trying with --user flag...
    pip install pyinstaller --user --quiet --disable-pip-version-check
)
echo  [OK] PyInstaller ready!

REM Build the EXE
echo.
echo [Step 3/4] Building EXE file...
echo  Please wait, this may take 1-2 minutes...
echo.
pyinstaller --onefile --windowed --name "PDF_Forensic_Sanitizer" --clean pdf_sanitizer_full.py

if errorlevel 1 (
    echo.
    echo  ERROR: Build failed!
    echo  Try running this script as Administrator.
    pause
    exit /b 1
)

REM Done
echo.
echo [Step 4/4] Cleaning up...
rmdir /s /q build 2>nul
del /q *.spec 2>nul

echo.
echo  ============================================================
echo   BUILD SUCCESSFUL!
echo  ============================================================
echo.
echo  Your EXE file is ready at:
echo.
echo    dist\PDF_Forensic_Sanitizer.exe
echo.
echo  HOW TO USE:
echo    - Drag and drop any PDF file onto the EXE
echo    - Or double-click to open GUI
echo    - Or run from command line: PDF_Forensic_Sanitizer.exe file.pdf
echo.
echo  The sanitized file will be saved as: filename_sanitized.pdf
echo.
echo  ============================================================
echo.

REM Open the dist folder
explorer dist

pause
