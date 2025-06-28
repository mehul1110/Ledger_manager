import subprocess
import sys
import os
import shutil

# Utility to run shell commands
def run(cmd, shell=True):
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=shell)
    if result.returncode != 0:
        print(f"Command failed: {cmd}")
        sys.exit(1)

# Step 1: Install required packages
run(f"{sys.executable} -m pip install --upgrade pip")
run(f"{sys.executable} -m pip install pyinstaller pillow mysql-connector-python tkcalendar")

# Step 1.5: Ensure latest PyInstaller for Python 3.10 compatibility
run(f"{sys.executable} -m pip install --upgrade pyinstaller")

# Step 2: Clean previous builds
for folder in ['dist', 'build']:
    if os.path.exists(folder):
        shutil.rmtree(folder)

# Step 3: Build the executable (force --clean and --noupx for PyInstaller reliability)
pyinstaller_cmd = (
    "pyinstaller --onefile --windowed --clean --noupx "
    "--icon=frontend/app_icon.ico "
    "--name=BAHI-KHATA frontend/app.py"
)
run(pyinstaller_cmd)

# Step 4: Copy resources
package_dir = os.path.join("dist", "BAHI-KHATA-Package")
os.makedirs(package_dir, exist_ok=True)
shutil.move(os.path.join("dist", "BAHI-KHATA.exe"), package_dir)

# Copy images and views
os.makedirs(os.path.join(package_dir, "frontend"), exist_ok=True)
os.makedirs(os.path.join(package_dir, "frontend", "views"), exist_ok=True)
for ext in ("jpg", "png"):
    for file in os.listdir("frontend"):
        if file.endswith(f".{ext}"):
            shutil.copy(os.path.join("frontend", file), os.path.join(package_dir, "frontend"))
for file in os.listdir("frontend/views"):
    if file.endswith(".py"):
        shutil.copy(os.path.join("frontend/views", file), os.path.join(package_dir, "frontend", "views"))

# Copy Python modules except create_icon.py
for file in os.listdir("."):
    if file.endswith(".py") and file != "create_icon.py" and file != "build_exe.py":
        shutil.copy(file, package_dir)

# Step 5: Offer to run the database setup script
print("\nBuild complete! Your package is in dist/BAHI-KHATA-Package/")
print("\nWould you like to run the database setup script now? (y/n)")
choice = input().strip().lower()
if choice == 'y':
    print("\nPlease enter your MySQL username (default: root): ", end='')
    mysql_user = input().strip() or 'root'
    print("Please enter your MySQL database name (default: ledger_db): ", end='')
    mysql_db = input().strip() or 'ledger_db'
    print(f"Please enter the MySQL password for {mysql_user}: ", end='')
    import getpass
    mysql_pass = getpass.getpass('')
    setup_cmd = f"mysql -u {mysql_user} -p{mysql_pass} {mysql_db} < setup_bahi_khata.sql"
    run(setup_cmd, shell=True)
    print("\nDatabase setup completed!")
else:
    print("\nYou can manually run the setup_bahi_khata.sql script later to initialize your database.")
