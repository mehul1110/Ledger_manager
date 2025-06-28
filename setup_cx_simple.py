from cx_Freeze import setup, Executable 
build_exe_options = { 
    "packages": ["os", "tkinter", "tkcalendar", "mysql.connector", "PIL", "openpyxl"], 
    "include_files": [("frontend/views", "views")] 
} 
setup( 
    name="BAHI-KHATA", 
    version="1.0", 
    description="Ledger Management App", 
    options={"build_exe": build_exe_options}, 
    executables=[Executable("frontend/app.py", target_name="BAHI-KHATA.exe")] 
) 
