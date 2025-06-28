import sys
import os

if not (sys.version_info.major == 3 and sys.version_info.minor == 9):
    sys.exit("ERROR: Please run this script with Python 3.9 to match cx_Freeze base executables.")

# Warn if a shadowing pathlib.py is found in site-packages
for p in sys.path:
    candidate = os.path.join(p, "pathlib.py")
    if os.path.exists(candidate):
        print(f"WARNING: Found shadowing pathlib.py at {candidate}. Please remove it to avoid import errors.")

from cx_Freeze import setup, Executable

# Add frontend to the path to help cx_Freeze resolve imports
sys.path.insert(0, 'frontend')

# Dependencies are automatically detected, but some modules need manual inclusion
build_exe_options = {
    "packages": [
        "os",
        "tkinter",
        "tkcalendar",
        "mysql.connector",
        "PIL",
        "frontend",
        "openpyxl"
    ],
    "include_files": [
        # App resources - copy to root for easy access
        ("frontend/app_icon.ico", "app_icon.ico"),
        ("frontend/bg_image.jpg", "bg_image.jpg"),
        ("frontend/left_logo.jpg", "left_logo.jpg"),
        ("frontend/right_logo.jpg", "right_logo.jpg"),
        # Also keep images in frontend folder for compatibility
        ("frontend/bg_image.jpg", "frontend/bg_image.jpg"),
        ("frontend/left_logo.jpg", "frontend/left_logo.jpg"),
        ("frontend/right_logo.jpg", "frontend/right_logo.jpg"),
        # Copy the views directory to the top level of the build
        ("frontend/views", "views"),
        # Root-level Python modules that might be missed
        "db_connect.py",
        "utils.py",
        "account_utils.py",
        "balance_utils.py",
        "journal_utils.py",
        "notification_utils.py",
        "role_permissions.py",
        "transaction_approver.py",
        "add_account.py",
        "add_payment.py",
        "add_receipt.py",
        "bring_forward.py",
        "brought_forward_balances.py",
        "depreciate_property.py",
        "ensure_account_types.py",
        "fd_approve_maturity.py",
        "fd_maturity_update.py",
        "list_sundry_credits.py",
        "monthly_balance_sheet_simple.py",
        "monthly_balance_sheet.py",
        "notification_system.py"
    ],
    "excludes": []
}

base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name="BAHI-KHATA",
    version="1.0",
    description="Ledger Management App",
    options={"build_exe": build_exe_options},
    executables=[Executable("frontend/app.py", base=base, icon="frontend/app_icon.ico", target_name="BAHI-KHATA.exe")]
)
