import sys
import os

# Add the executable directory to Python path so modules can be imported
if hasattr(sys, '_MEIPASS'):
    # Running in PyInstaller bundle
    sys.path.insert(0, sys._MEIPASS)
    sys.path.insert(0, os.path.join(sys._MEIPASS, '.'))
else:
    # Running in development
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
