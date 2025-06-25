# Basic Tkinter App Structure
# This is the main entry point for your frontend GUI

import tkinter as tk
from PIL import Image, ImageTk
from views.add_payment_view import show_add_payment_form
from views.add_account_view import show_add_account_form
from views.add_receipt_view import show_add_receipt_form
from views.view_transactions_menu import show_view_transactions_menu
from views.payments_view import show_payments_view
from views.receipts_view import show_receipts_view
from views.accounts_view import show_accounts_view
from views.journal_entries_view import show_journal_entries_view
from views.monthly_balance_sheet_view import show_monthly_balance_sheet_ui
from views.fd_details_view import show_fd_details_view
from views.property_details_view import show_property_details_view
from views.approval_view import show_approval_view
from transaction_approver import get_pending_transaction_count
from views.comparison_view import show_comparison_view
from simple_login import show_login_dialog


class BookkeepingApp:
    def __init__(self, root, user_info=None):
        self.root = root
        self.user_info = user_info or {'username': 'guest', 'role': 'viewer', 'user_id': None}
        self.root.title(f"BAHI-KHATA App - Welcome {self.user_info['username']} ({self.user_info['role'].title()})")
        self.root.geometry("900x600")
        self._last_size = (self.root.winfo_width(), self.root.winfo_height())
        self.sidebar = None
        self.current_view_refresh_callback = None # To hold the refresh function for the current view
        self.set_background()
        self.create_widgets()
        self.root.bind('<Configure>', self._on_resize)

    def set_background(self):
        # Load and set a background image as a label covering the window, resizing dynamically
        try:
            width = self.root.winfo_width() or 900
            height = self.root.winfo_height() or 600
            img = Image.open("frontend/bg_image.jpg")
            img = img.resize((width, height), Image.LANCZOS)
            self.bg_photo = ImageTk.PhotoImage(img)
            if hasattr(self, 'bg_label') and self.bg_label.winfo_exists():
                self.bg_label.config(image=self.bg_photo)
            else:
                self.bg_label = tk.Label(self.root, image=self.bg_photo, borderwidth=0, highlightthickness=0)
                self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
                self.bg_label.lower()
        except Exception as e:
            print(f"Background image error: {e}")

    def create_sidebar(self):
        self.sidebar = tk.Frame(self.root, bg='#f0f0f0', width=250, relief='sunken', borderwidth=1)
        
        close_button = tk.Button(self.sidebar, text="X", command=self.toggle_sidebar, font=("Arial", 12, "bold"), bg='#f0f0f0', relief='flat')
        close_button.pack(anchor='ne', pady=5, padx=5)

        tk.Label(self.sidebar, text="Notifications", font=("Arial", 16, "bold"), bg='#f0f0f0').pack(pady=10)

        pending_count = get_pending_transaction_count()
        approval_button_text = f"Pending Approvals ({pending_count})"
        self.approval_button = tk.Button(self.sidebar, text=approval_button_text, command=self.show_approval_view, font=("Arial", 12), bg='#e0e0e0')
        self.approval_button.pack(pady=10, padx=10, fill='x')

        if pending_count == 0:
            tk.Label(self.sidebar, text="No new notifications.", font=("Arial", 12), bg='#f0f0f0').pack(pady=10, padx=10)

        # Add a periodic check to update the count
        self.root.after(30000, self.update_pending_count) # Check every 30 seconds

    def update_pending_count(self):
        """Periodically updates the pending transaction count in the sidebar."""
        if self.sidebar and self.sidebar.winfo_exists():
            pending_count = get_pending_transaction_count()
            approval_button_text = f"Pending Approvals ({pending_count})"
            self.approval_button.config(text=approval_button_text)
        self.root.after(30000, self.update_pending_count) # Reschedule the check

    def toggle_sidebar(self):
        try:
            # If sidebar exists and is visible, hide it and stop.
            if self.sidebar and self.sidebar.winfo_ismapped():
                self.sidebar.place_forget()
                return
        except tk.TclError:
            # This can happen if the widget was destroyed externally.
            # In that case, reset self.sidebar so it can be recreated.
            self.sidebar = None

        # If we reached here, the sidebar is hidden or needs to be created.
        if self.sidebar is None:
            self.create_sidebar()
        
        # Show the sidebar.
        self.sidebar.place(x=0, y=0, relheight=1)
        self.sidebar.lift()

    def get_responsive_fonts(self):
        # Calculate and cache all font sizes based on window width
        width = self.root.winfo_width() or 900
        scale = width / 900
        # Clamp scale to avoid fonts getting too small or too large
        scale = max(1.0, min(scale, 1.25))  # Minimum 1.0, maximum 1.25
        self.fonts = {
            'title': ("Georgia", max(int(32 * scale), 18), 'bold italic'),
            'label': ("Arial", max(int(20 * scale), 13)),
            'entry': ("Arial", max(int(18 * scale), 13)),
            'button': ("Arial", max(int(18 * scale), 13)),
        }

    def create_widgets(self):
        # Clear the window before adding new widgets
        for widget in self.root.winfo_children():
            widget.destroy()
        self.set_background()

        # Hamburger button for sidebar
        hamburger_font = ("Arial", 20)
        # Positioned next to the left logo, which is 90x90 at (10,10)
        hamburger_button = tk.Button(self.root, text="☰", command=self.toggle_sidebar, font=hamburger_font, borderwidth=0, highlightthickness=0, bg='white', relief='flat', activebackground='white')
        hamburger_button.place(x=115, y=15)

        self.get_responsive_fonts()
        title_font = ("Georgia", max(int(32 * (self.root.winfo_width() / 900)), 18), 'bold italic')
        btn_font = ("Segoe UI", max(int(18 * (self.root.winfo_width() / 900)), 13), 'bold')
        button_names = [
            ("Add Payer/Payee", self.show_add_account_form),
            ("Add Transactions", self.show_add_transactions_menu),
            ("View Transactions", self.show_view_transactions_menu)
        ]
        tk.Label(self.root, text="The BAHIKHATA App!", font=title_font, bg="white", fg="#222").pack(pady=(40, 5), padx=30)
        subheading_font = ("Segoe UI", max(int(12 * (self.root.winfo_width() / 900)), 8), 'italic')
        tk.Label(self.root, text="EME Journal Accounts Management System.", font=subheading_font, bg="white", fg="#555").pack(pady=(0, 25), padx=30)
        import tkinter.ttk as ttk
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Modern.TButton', font=btn_font, padding=12, relief='flat', background='#ffffff', foreground='#222', borderwidth=0, focusthickness=3, focuscolor='none')
        style.map('Modern.TButton', background=[('active', '#e0e0e0')])
        style.configure('Hover.TButton', font=btn_font, padding=12, relief='flat', background='#ffffff', foreground='#222', borderwidth=0)
        style.map('Hover.TButton',
            background=[('active', '#e0e0e0')],
            relief=[('active', 'raised')],
            highlightthickness=[('active', 2)]
        )
        button_panel = tk.Frame(self.root, bg='#ffffff', bd=0, highlightthickness=0)
        button_panel.pack(pady=(0, 0))
        def on_enter(e):
            e.widget.configure(style='Hover.TButton')
        def on_leave(e):
            e.widget.configure(style='Modern.TButton')
        btn_width = 22  # Fixed width for all buttons
        for text, cmd in button_names:
            btn = ttk.Button(button_panel, text=text, style='Modern.TButton', command=cmd, width=btn_width)
            btn.pack(pady=14, padx=40)
            btn.bind('<Enter>', on_enter)
            btn.bind('<Leave>', on_leave)
        button_panel.update_idletasks()
        min_width = 340
        button_panel.config(width=max(button_panel.winfo_width(), min_width))
        footer_font = ("Arial", 10, 'bold italic')
        footer_label = tk.Label(self.root, text="Developed by Mehul Ashra during Summer Internship at FEL, MCEME", font=footer_font, fg="#666", anchor='e', justify='right', borderwidth=0, highlightthickness=0)
        footer_label.place(relx=1.0, rely=1.0, anchor='se', x=-20, y=-8)
        try:
            left_logo_img = Image.open("frontend/left_logo.jpg")
            left_logo_img = left_logo_img.resize((90, 90), Image.LANCZOS)
            self.left_logo_photo = ImageTk.PhotoImage(left_logo_img)
            left_logo_label = tk.Label(self.root, image=self.left_logo_photo, borderwidth=0, highlightthickness=0)
            left_logo_label.place(x=10, y=10)
        except Exception as e:
            print(f"Left logo error: {e}")
        try:
            right_logo_img = Image.open("frontend/right_logo.jpg")
            right_logo_img = right_logo_img.resize((90, 90), Image.LANCZOS)
            self.right_logo_photo = ImageTk.PhotoImage(right_logo_img)
            right_logo_label = tk.Label(self.root, image=self.right_logo_photo, borderwidth=0, highlightthickness=0)
            right_logo_label.place(relx=1.0, x=0, y=10, anchor='ne')
        except Exception as e:
            print(f"Right logo error: {e}")

    def show_add_transactions_menu(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.set_background()
        self.get_responsive_fonts()
        import tkinter.ttk as ttk
        # Use the same font and style as main menu
        title_font = ("Georgia", max(int(32 * (self.root.winfo_width() / 900)), 18), 'bold italic')
        btn_font = ("Segoe UI", max(int(18 * (self.root.winfo_width() / 900)), 13), 'bold')
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Modern.TButton', font=btn_font, padding=12, relief='flat', background='#ffffff', foreground='#222', borderwidth=0, focusthickness=3, focuscolor='none')
        style.map('Modern.TButton', background=[('active', '#e0e0e0')])
        style.configure('Hover.TButton', font=btn_font, padding=12, relief='flat', background='#ffffff', foreground='#222', borderwidth=0)
        style.map('Hover.TButton',
            background=[('active', '#e0e0e0')],
            relief=[('active', 'raised')],
            highlightthickness=[('active', 2)]
        )
        # Go Back button at top left
        tk.Button(self.root, text="\u2190 Go Back", command=self.show_main_menu, font=btn_font, bg='white', relief='flat', borderwidth=2, highlightbackground='#222').place(x=10, y=10)
        # Center frame for title and buttons
        center_frame = tk.Frame(self.root, bg='#ffffff', bd=0, highlightthickness=0)
        center_frame.place(relx=0.5, rely=0.5, anchor='center')
        tk.Label(center_frame, text="Add Transactions", font=title_font, bg="white").pack(pady=(0, 20))
        btn_frame = tk.Frame(center_frame, bg='#ffffff', bd=0, highlightthickness=0)
        btn_frame.pack()
        def on_enter(e):
            e.widget.configure(style='Hover.TButton')
        def on_leave(e):
            e.widget.configure(style='Modern.TButton')
        btn_receipt = ttk.Button(btn_frame, text="Add Receipt(incoming)", command=self.show_add_receipt_form, style='Modern.TButton', width=22)
        btn_receipt.pack(pady=7)
        btn_receipt.bind('<Enter>', on_enter)
        btn_receipt.bind('<Leave>', on_leave)
        btn_payment = ttk.Button(btn_frame, text="Add Payment(outgoing)", command=self.show_add_payment_form, style='Modern.TButton', width=22)
        btn_payment.pack(pady=7)
        btn_payment.bind('<Enter>', on_enter)
        btn_payment.bind('<Leave>', on_leave)

    def _on_resize(self, event):
        # Only update background and fonts, do not reload widgets
        new_size = (self.root.winfo_width(), self.root.winfo_height())
        if abs(new_size[0] - self._last_size[0]) > 5 or abs(new_size[1] - self._last_size[1]) > 5:
            self._last_size = new_size
            self.set_background()
            self.get_responsive_fonts()
        # self.create_widgets()  # Removed to prevent reload on resize

    def show_main_menu(self):
        self.current_view_refresh_callback = None # No specific data view to refresh from main menu
        self.create_widgets()

    def show_add_receipt_form(self):
        from views.add_receipt_view import show_add_receipt_form
        show_add_receipt_form(self, go_back_callback=self.show_add_transactions_menu)

    def show_add_account_form(self):
        from views.add_account_view import show_add_account_form
        show_add_account_form(self)

    def show_add_payment_form(self):
        from views.add_payment_view import show_add_payment_form
        show_add_payment_form(self, go_back_callback=self.show_add_transactions_menu)

    def show_view_transactions_menu(self):
        show_view_transactions_menu(self)

    def show_comparison_view(self):
        show_comparison_view(self)

    def show_payments_view(self):
        self.current_view_refresh_callback = self.show_payments_view
        show_payments_view(self)

    def show_receipts_view(self):
        self.current_view_refresh_callback = self.show_receipts_view
        show_receipts_view(self)

    def show_accounts_view(self):
        self.current_view_refresh_callback = self.show_accounts_view
        show_accounts_view(self)

    def show_journal_entries_view(self):
        self.current_view_refresh_callback = self.show_journal_entries_view
        show_journal_entries_view(self)

    def show_monthly_balance_sheet_view(self):
        self.current_view_refresh_callback = self.show_monthly_balance_sheet_view
        for widget in self.root.winfo_children():
            widget.destroy()
        self.set_background()
        frame = tk.Frame(self.root, bg='white')
        frame.pack(fill="both", expand=True)
        show_monthly_balance_sheet_ui(frame, go_back_callback=self.show_view_transactions_menu)

    def show_fd_details_view(self):
        self.current_view_refresh_callback = self.show_fd_details_view
        show_fd_details_view(self)

    def show_property_details_view(self):
        self.current_view_refresh_callback = self.show_property_details_view
        show_property_details_view(self)

    def show_approval_view(self):
        show_approval_view(self, on_success_callback=self.current_view_refresh_callback)

    def show_placeholder_view(self, name):
        self.current_view_refresh_callback = None
        for widget in self.root.winfo_children():
            widget.destroy()
        self.set_background()
        self.get_responsive_fonts()
        label_font = self.fonts['label']
        button_font = self.fonts['button']
        tk.Button(self.root, text="← Go Back", command=self.show_view_transactions_menu, font=button_font).pack(anchor='w', padx=10, pady=10)
        tk.Label(self.root, text=f"{name} view coming soon...", font=label_font, bg="white").pack(pady=40)

if __name__ == "__main__":
    import sys
    import traceback
    import logging
    from datetime import datetime
    import os
    
    # Set up logging to both file and console - use single error.log file
    log_filename = "error.log"
    logging.basicConfig(
        level=logging.INFO,  # Changed to INFO to capture more details
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger(__name__)
    
    try:
        # Log system information for debugging
        logger.info("="*60)
        logger.info("BAHI-KHATA Application Starting")
        logger.info("="*60)
        logger.info(f"Python version: {sys.version}")
        logger.info(f"Working directory: {os.getcwd()}")
        logger.info(f"Script path: {os.path.abspath(__file__)}")
        logger.info(f"Python path: {sys.path}")
        logger.info("-"*60)
        
        logger.info("Testing critical imports...")
        
        # Test imports that commonly cause issues
        try:
            import tkinter as tk_test
            logger.info("✓ tkinter imported successfully")
        except Exception as e:
            logger.error(f"✗ tkinter import failed: {e}")
            raise
            
        try:
            from PIL import Image, ImageTk
            logger.info("✓ PIL/Pillow imported successfully")
        except Exception as e:
            logger.error(f"✗ PIL/Pillow import failed: {e}")
            raise
            
        try:
            import mysql.connector
            logger.info("✓ mysql.connector imported successfully")
        except Exception as e:
            logger.error(f"✗ mysql.connector import failed: {e}")
            raise
        
        logger.info("✓ All critical imports successful")
        logger.info("-"*60)
        
        logger.info("Creating Tkinter root window...")
        root = tk.Tk()
        logger.info("✓ Tkinter root window created successfully")
        
        # Set up the main window but don't show it yet
        logger.info("Configuring main window...")
        root.title("BAHI-KHATA App")
        root.geometry("900x600")
        root.withdraw()  # Hide the main window initially
        logger.info("✓ Main window configured and hidden")
        
        # Show login dialog
        logger.info("Attempting to show login dialog...")
        user_info = show_login_dialog(root)
        if user_info:
            logger.info(f"✓ Login successful for user: {user_info['username']} (Role: {user_info['role']})")
            # Login successful, show main application
            root.deiconify()  # Show the main window
            logger.info("Creating BookkeepingApp instance...")
            app = BookkeepingApp(root, user_info)
            logger.info("✓ BookkeepingApp instance created successfully")
            logger.info("Starting main application loop...")
            root.mainloop()
            logger.info("Application closed normally")
        else:
            logger.info("Login cancelled or failed, exiting application")
            # Login cancelled or failed, exit
            root.quit()
            root.destroy()
            
    except Exception as e:
        error_msg = f"Application startup failed: {str(e)}"
        full_traceback = traceback.format_exc()
        
        # Log to file and console
        logger.error("="*60)
        logger.error("CRITICAL ERROR DURING STARTUP")
        logger.error("="*60)
        logger.error(error_msg)
        logger.error("Full traceback:")
        logger.error(full_traceback)
        logger.error("="*60)
        
        # Also print to stdout for immediate visibility
        print(f"\n{'='*60}")
        print("BAHI-KHATA APPLICATION ERROR")
        print(f"{'='*60}")
        print(f"Error: {error_msg}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Log file: {log_filename}")
        print("\nFull error details:")
        print(full_traceback)
        print(f"{'='*60}")
        print("\nTroubleshooting steps:")
        print("1. Run 'diagnose.bat' for detailed diagnostics")
        print("2. Ensure MySQL server is running")
        print("3. Check database credentials in db_connect.py")
        print("4. Install missing packages: pip install -r requirements.txt")
        print(f"{'='*60}")
        
        # Try to show a simple error dialog if tkinter is available
        try:
            import tkinter.messagebox as messagebox
            error_window = tk.Tk()
            error_window.withdraw()
            messagebox.showerror(
                "Application Error", 
                f"The application failed to start.\n\nError: {error_msg}\n\nCheck the log file: {log_filename}\n\nRun 'diagnose.bat' for detailed troubleshooting."
            )
            error_window.destroy()
        except:
            # If even the error dialog fails, just continue with console output
            pass
        
        # Keep console open for a few seconds so user can see the error
        try:
            input("\nPress Enter to close...")
        except:
            import time
            time.sleep(5)
        
        sys.exit(1)
