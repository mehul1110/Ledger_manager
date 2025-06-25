# BAHI-KHATA App - Executable Build Instructions

## Creating an Executable

### Step 1: Prepare Your Logo (Optional)
If you have a logo image you want to use for your app:
1. Place your logo image (PNG, JPG, etc.) in the project folder
2. Run: `python create_icon.py your_logo_image.png`
3. This will create `frontend/app_icon.ico` for your executable

### Step 2: Build the Executable
Simply double-click the `build_app.bat` file or run it from command prompt:
```
build_app.bat
```

This script will:
- Install required packages (PyInstaller, Pillow, etc.)
- Clean previous builds
- Create a single executable file

### Step 3: Find Your Executable
After successful build, your executable will be located at:
```
dist/BAHI-KHATA.exe
```

## Distribution
- The generated EXE file is standalone and can run on any Windows computer
- No need to install Python or dependencies on target computers
- Simply copy `BAHI-KHATA.exe` to the target computer and run it

## Troubleshooting

### Common Issues:
1. **"Python not found"**: Install Python from python.org
2. **"Permission denied"**: Run command prompt as Administrator
3. **"Module not found"**: The build script will install required packages automatically

### Manual Build (if batch file doesn't work):
```bash
pip install pyinstaller pillow mysql-connector-python
pyinstaller app.spec
```

## File Structure After Build:
```
dist/
└── BAHI-KHATA.exe    (Your final executable)

build/                 (Temporary build files - can be deleted)
```

## Notes:
- The executable will be quite large (50-100MB) because it includes Python runtime
- First startup might be slower as the executable extracts itself
- Antivirus software might flag the EXE initially (this is normal for PyInstaller executables)
