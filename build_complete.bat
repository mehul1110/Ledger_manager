@echo off
echo ================================================
echo     BAHI-KHATA App - Complete Build Script
echo ================================================
echo.

REM Clean previous builds
if exist "dist" rmdir /s /q dist
if exist "build" rmdir /s /q build

echo [1/3] Building base executable...
pyinstaller --onefile --windowed --icon=frontend/app_icon.ico --name=BAHI-KHATA frontend/app.py

echo.
echo [2/3] Creating deployment package...
mkdir dist\BAHI-KHATA-Package 2>nul
move dist\BAHI-KHATA.exe dist\BAHI-KHATA-Package\

echo Copying essential files...
mkdir dist\BAHI-KHATA-Package\frontend 2>nul
mkdir dist\BAHI-KHATA-Package\frontend\views 2>nul

copy frontend\*.jpg dist\BAHI-KHATA-Package\frontend\ >nul
copy frontend\*.png dist\BAHI-KHATA-Package\frontend\ >nul
copy frontend\views\*.py dist\BAHI-KHATA-Package\frontend\views\ >nul

echo Copying Python modules...
for %%f in (*.py) do (
    if not "%%f"=="create_icon.py" (
        copy "%%f" dist\BAHI-KHATA-Package\ >nul
    )
)

echo.
echo [3/3] Creating README for distribution...
echo BAHI-KHATA Bookkeeping Application > dist\BAHI-KHATA-Package\README.txt
echo. >> dist\BAHI-KHATA-Package\README.txt
echo To run the application: >> dist\BAHI-KHATA-Package\README.txt
echo 1. Double-click BAHI-KHATA.exe >> dist\BAHI-KHATA-Package\README.txt
echo 2. Make sure all files in this folder stay together >> dist\BAHI-KHATA-Package\README.txt
echo. >> dist\BAHI-KHATA-Package\README.txt
echo System Requirements: >> dist\BAHI-KHATA-Package\README.txt
echo - Windows 7 or later >> dist\BAHI-KHATA-Package\README.txt
echo - No additional software needed >> dist\BAHI-KHATA-Package\README.txt
echo. >> dist\BAHI-KHATA-Package\README.txt
echo Developed by Mehul Ashra during Summer Internship at FEL, MCEME >> dist\BAHI-KHATA-Package\README.txt

echo.
echo ================================================
echo        BUILD COMPLETE!
echo ================================================
echo.
echo Your complete application package is ready in:
echo dist\BAHI-KHATA-Package\
echo.
echo The package contains:
echo - BAHI-KHATA.exe (main application)
echo - All required images and configuration files
echo - README.txt with instructions
echo.
echo You can zip this folder and distribute it to users.
echo.
pause
