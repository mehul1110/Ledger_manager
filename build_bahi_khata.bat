@echo off
REM BAHI-KHATA Executable Build Script
REM This script builds the executable using PyInstaller and the .spec file

REM Clean previous builds
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
if exist __pycache__ rmdir /s /q __pycache__

REM Ensure latest pip and PyInstaller
python -m pip install --upgrade pip
python -m pip install --upgrade pyinstaller

REM Build the executable using the .spec file (no --noupx, no --clean with .spec)
pyinstaller BAHI-KHATA.spec

REM Move the built exe to a package folder
mkdir dist\BAHI-KHATA-Package 2>nul
move dist\BAHI-KHATA.exe dist\BAHI-KHATA-Package\

REM Copy resources
mkdir dist\BAHI-KHATA-Package\frontend 2>nul
mkdir dist\BAHI-KHATA-Package\frontend\views 2>nul
copy frontend\*.jpg dist\BAHI-KHATA-Package\frontend\ >nul
copy frontend\*.png dist\BAHI-KHATA-Package\frontend\ >nul
copy frontend\views\*.py dist\BAHI-KHATA-Package\frontend\views\ >nul

REM Copy Python modules except create_icon.py and build_exe.py
for %%f in (*.py) do (
    if /I not "%%f"=="create_icon.py" if /I not "%%f"=="build_exe.py" (
        copy "%%f" dist\BAHI-KHATA-Package\ >nul
    )
)

REM Copy SQL setup script
copy setup_bahi_khata.sql dist\BAHI-KHATA-Package\ >nul

REM Prompt for MySQL credentials and run SQL setup
set /p MYSQL_USER=Enter MySQL username (default: root): 
if "%MYSQL_USER%"=="" set MYSQL_USER=root
set /p MYSQL_DB=Enter database name to setup (default: ledger_db): 
if "%MYSQL_DB%"=="" set MYSQL_DB=ledger_db
set /p MYSQL_PASS=Enter MySQL password for %MYSQL_USER%: 

cd dist\BAHI-KHATA-Package
mysql -u %MYSQL_USER% -p%MYSQL_PASS% %MYSQL_DB% < setup_bahi_khata.sql
cd ..\..

echo.
echo Build complete! Your package is in dist\BAHI-KHATA-Package\
pause
