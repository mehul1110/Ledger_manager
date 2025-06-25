@echo off
echo ================================================
echo    BAHI-KHATA App - Fixed Module Import Build
echo ================================================
echo.

REM Clean previous builds
echo [1/4] Cleaning previous builds...
if exist "dist" rmdir /s /q dist 2>nul
if exist "build" rmdir /s /q build 2>nul

echo [2/4] Building executable (this may take a few minutes)...
pyinstaller --onefile --windowed --icon=frontend/app_icon.ico --name=BAHI-KHATA --add-data "frontend;frontend" --add-data "*.py;." frontend/app.py

echo.
echo [3/4] Checking build result...
if not exist "dist\BAHI-KHATA.exe" (
    echo ERROR: Build failed!
    pause
    exit /b 1
)

echo [4/4] Creating deployment package...
mkdir dist\BAHI-KHATA-Package 2>nul
move dist\BAHI-KHATA.exe dist\BAHI-KHATA-Package\

echo Copying all Python files to package directory...
for %%f in (*.py) do (
    if not "%%f"=="create_icon.py" (
        copy "%%f" dist\BAHI-KHATA-Package\ >nul
    )
)

echo Copying frontend directory...
xcopy frontend dist\BAHI-KHATA-Package\frontend\ /E /I /Q >nul

echo Creating README...
echo BAHI-KHATA Bookkeeping Application > dist\BAHI-KHATA-Package\README.txt
echo. >> dist\BAHI-KHATA-Package\README.txt
echo IMPORTANT: Keep all files in this folder together! >> dist\BAHI-KHATA-Package\README.txt
echo. >> dist\BAHI-KHATA-Package\README.txt
echo To run: Double-click BAHI-KHATA.exe >> dist\BAHI-KHATA-Package\README.txt
echo. >> dist\BAHI-KHATA-Package\README.txt
echo System Requirements: Windows 7 or later >> dist\BAHI-KHATA-Package\README.txt
echo No additional software needed >> dist\BAHI-KHATA-Package\README.txt

echo.
echo ================================================
echo        BUILD SUCCESSFUL!
echo ================================================
echo.
echo Your application package is ready in:
echo dist\BAHI-KHATA-Package\
echo.
echo NOTE: The executable needs to run from the package folder
echo to find all the Python modules and data files.
echo.
pause
