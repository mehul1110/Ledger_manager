@echo off
echo ================================================
echo        BAHI-KHATA App Build Script
echo ================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python and try again.
    pause
    exit /b 1
)

echo [1/4] Installing required packages...
pip install pyinstaller pillow mysql-connector-python

echo.
echo [2/4] Checking for app icon...
if not exist "frontend\app_icon.ico" (
    echo WARNING: app_icon.ico not found in frontend folder
    echo You can create one by running: python create_icon.py your_logo_image.png
    echo Using default icon for now...
)

echo.
echo [3/4] Cleaning previous build...
if exist "dist" rmdir /s /q dist
if exist "build" rmdir /s /q build

echo.
echo [4/4] Building executable...
pyinstaller app.spec

echo.
if exist "dist\BAHI-KHATA.exe" (
    echo ================================================
    echo        BUILD SUCCESSFUL!
    echo ================================================
    echo.
    echo Your executable is ready: dist\BAHI-KHATA.exe
    echo.
    echo You can now distribute this single EXE file to run your app
    echo on any Windows computer without Python installed.
    echo.
) else (
    echo ================================================
    echo        BUILD FAILED!
    echo ================================================
    echo Please check the error messages above.
)

pause
