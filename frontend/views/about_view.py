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
    
    # Scrollable Frame
    scrollable_frame = tk.Frame(app.root, bg="white", relief="groove", borderwidth=2)
    scrollable_frame.place(relx=0.5, rely=0.5, anchor="center", width=900, height=600)

    canvas = tk.Canvas(scrollable_frame, bg="white")
    scrollbar = tk.Scrollbar(scrollable_frame, orient="vertical", command=canvas.yview)
    scrollable_content = tk.Frame(canvas, bg="white")

    scrollable_content.bind(
        "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_content, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Title
    tk.Label(scrollable_content, text="About BAHI-KHATA", font=("Arial", 36, "bold"), bg="white", fg="darkblue").pack(pady=(20, 10))

    # Application information
    about_text = """BAHI-KHATA - Your Trusted Bookkeeping Companion

Version: 2.0 (July 2025)

BAHI-KHATA is a comprehensive double-entry bookkeeping system designed to simplify financial management for individuals and businesses alike. With a modern interface and powerful features, it ensures accuracy and efficiency in managing your accounts."""

    tk.Label(scrollable_content, text=about_text, font=("Arial", 16), bg="white", justify='center', wraplength=850, fg="black").pack(pady=(10, 20))

    # New Updates Section
    tk.Label(scrollable_content, text="New Updates:", font=("Arial", 20, "bold"), bg="lightblue", fg="darkblue").pack(anchor="w", pady=(10, 5))
    updates_text = """• Enhanced user interface with responsive design
• Advanced reporting tools with customizable templates
• Integration with third-party payment gateways
• Real-time notifications for approvals and updates
• Improved security with two-factor authentication
• Multi-language support for global users"""
    tk.Label(scrollable_content, text=updates_text, font=("Arial", 14), bg="lightblue", justify='left', wraplength=850).pack(anchor="w", pady=(0, 20))

    # Core Features Section
    tk.Label(scrollable_content, text="Core Features:", font=("Arial", 20, "bold"), bg="lightgreen", fg="darkgreen").pack(anchor="w", pady=(10, 5))
    features_text = """• Double-entry accounting system
• Transaction approval workflow
• Role-based permissions
• Financial reports and balance sheets
• Fixed deposits and property management
• Journal entries tracking
• Automated depreciation calculations"""
    tk.Label(scrollable_content, text=features_text, font=("Arial", 14), bg="lightgreen", justify='left', wraplength=850).pack(anchor="w", pady=(0, 20))

    # Footer
    tk.Label(scrollable_content, text="Developed with Python and Tkinter", font=("Arial", 12, "italic"), bg="white", fg="gray").pack(pady=(10, 5))
    tk.Label(scrollable_content, text="© 2025 BAHI-KHATA | All Rights Reserved", font=("Arial", 12), bg="white", fg="gray").pack(pady=(0, 20))
