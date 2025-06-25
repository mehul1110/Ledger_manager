@echo off
echo ================================================
echo     BAHI-KHATA - Quick Update Build
echo ================================================
echo.

echo [1/2] Cleaning previous build...
if exist "dist\BAHI-KHATA.exe" del "dist\BAHI-KHATA.exe" 2>nul
if exist "build" rmdir /s /q build 2>nul

echo [2/2] Building updated executable...
pyinstaller app.spec

if exist "dist\BAHI-KHATA.exe" (
    echo.
    echo ✅ BUILD SUCCESSFUL!
    echo Updated executable: dist\BAHI-KHATA.exe
    echo.
    echo Ready to test your changes!
) else (
    echo.
    echo ❌ BUILD FAILED!
    echo Check the error messages above.
)

echo.
pause
