#!/usr/bin/env python3
"""
Minimal GUI test to check if Tkinter can initialize properly.
This test creates a simple window to verify GUI functionality.
"""

import sys
import traceback
from datetime import datetime

def test_gui():
    """Test basic GUI initialization."""
    print("Testing GUI initialization...")
    
    try:
        import tkinter as tk
        print("✓ Tkinter imported successfully")
        
        # Test root window creation
        root = tk.Tk()
        print("✓ Root window created")
        
        root.title("GUI Test")
        root.geometry("300x200")
        print("✓ Window properties set")
        
        # Test basic widgets
        label = tk.Label(root, text="GUI Test Successful!")
        label.pack(pady=50)
        print("✓ Label widget created")
        
        button = tk.Button(root, text="Close", command=root.quit)
        button.pack(pady=10)
        print("✓ Button widget created")
        
        print("✓ GUI test window will appear - click 'Close' to continue")
        
        # Show window briefly
        root.after(3000, root.quit)  # Auto-close after 3 seconds
        root.mainloop()
        root.destroy()
        
        print("✓ GUI test completed successfully")
        return True
        
    except Exception as e:
        print(f"✗ GUI test failed: {str(e)}")
        print(traceback.format_exc())
        return False

def test_pil():
    """Test PIL/Pillow image library."""
    print("\nTesting PIL/Pillow...")
    
    try:
        from PIL import Image, ImageTk
        print("✓ PIL/Pillow imported successfully")
        
        # Try to create a simple image
        img = Image.new('RGB', (100, 100), color='red')
        print("✓ Image creation test passed")
        
        return True
        
    except Exception as e:
        print(f"✗ PIL/Pillow test failed: {str(e)}")
        return False

def main():
    print("="*50)
    print("BAHI-KHATA GUI Test")
    print("="*50)
    print(f"Test time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    tests_passed = 0
    total_tests = 0
    
    # Test GUI
    total_tests += 1
    if test_gui():
        tests_passed += 1
    
    # Test PIL
    total_tests += 1
    if test_pil():
        tests_passed += 1
    
    print("\n" + "="*50)
    print(f"Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("✓ All GUI tests passed!")
    else:
        print("✗ Some tests failed. Check error messages above.")
    
    return tests_passed == total_tests

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Test script error: {str(e)}")
        print(traceback.format_exc())
    finally:
        input("\nPress Enter to close...")
