import tkinter as tk
from PIL import Image, ImageTk
import os

def show_about_view(app):
    """Show the About page with application information."""
    app.current_view_refresh_callback = None
    for widget in app.root.winfo_children():
        widget.destroy()
    app.set_background()
    app.get_responsive_fonts()
    label_font = app.fonts['label']
    button_font = app.fonts['button']
    
    # Back button
    tk.Button(app.root, text="← Go Back", command=app.show_main_menu, font=button_font, bg='white', relief='flat').place(x=10, y=10)
    
    # Add logos back
    try:
        left_logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "left_logo.jpg")
        left_logo_img = Image.open(left_logo_path)
        left_logo_img = left_logo_img.resize((90, 90), Image.LANCZOS)
        app.left_logo_photo = ImageTk.PhotoImage(left_logo_img)
        left_logo_label = tk.Label(app.root, image=app.left_logo_photo, borderwidth=0, highlightthickness=0)
        left_logo_label.place(x=10, y=60)  # Move down to avoid overlap with back button
    except Exception as e:
        print(f"Left logo error: {e}")
    
    try:
        right_logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "right_logo.jpg")
        right_logo_img = Image.open(right_logo_path)
        right_logo_img = right_logo_img.resize((90, 90), Image.LANCZOS)
        app.right_logo_photo = ImageTk.PhotoImage(right_logo_img)
        right_logo_label = tk.Label(app.root, image=app.right_logo_photo, borderwidth=0, highlightthickness=0)
        right_logo_label.place(relx=1.0, x=0, y=10, anchor='ne')
    except Exception as e:
        print(f"Right logo error: {e}")
    
    # About content frame - centered
    about_frame = tk.Frame(app.root, bg="white", padx=20, pady=20)
    about_frame.place(relx=0.5, rely=0.5, anchor='center', width=600, height=400)
    
    # Title
    tk.Label(about_frame, text="About BAHI-KHATA", font=("Arial", 20, "bold"), bg="white").pack(pady=(0, 20))
    
    # Application information
    about_text = """BAHI-KHATA - Bookkeeping Application

Version: 1.0
        
A comprehensive double-entry bookkeeping system designed for
managing financial transactions, accounts, and generating reports.

Features:
• Double-entry accounting system
• Transaction approval workflow
• Role-based permissions
• Financial reports and balance sheets
• Fixed deposits and property management
• Journal entries tracking

Developed with Python and Tkinter for a clean, user-friendly interface."""
    
    tk.Label(about_frame, text=about_text, font=("Arial", 12), bg="white", justify='left').pack(pady=10)
    
    # Additional info
    tk.Label(about_frame, text="© 2024 BAHI-KHATA", font=("Arial", 10), bg="white", fg="gray").pack(side='bottom', pady=(20, 0))
