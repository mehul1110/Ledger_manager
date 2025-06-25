import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import tkinter as tk
import db_connect
import tkinter.ttk as ttk

def show_view_transactions_menu(app):
    for widget in app.root.winfo_children():
        widget.destroy()
    app.set_background()
    app.get_responsive_fonts()
    label_font = app.fonts['label']
    btn_font = app.fonts['button']
    tk.Button(app.root, text="← Go Back", command=app.show_main_menu, font=btn_font).pack(anchor='w', padx=10, pady=10)
    tk.Label(app.root, text="View Transactions", font=label_font, bg="white").pack(pady=20)
    
    option_frame = tk.Frame(app.root, bg='', highlightthickness=0, bd=0)
    option_frame.pack(pady=10, expand=True)

    options = [
        ("Receipts", app.show_receipts_view),
        ("Payments", app.show_payments_view),
        ("Accounts", app.show_accounts_view),
        ("Journal Entries", app.show_journal_entries_view),
        ("FD Details", app.show_fd_details_view),
        ("Property Details", app.show_property_details_view),
        ("Monthly Balance Sheet", app.show_monthly_balance_sheet_view),
        ("Comparison", app.show_comparison_view)
    ]

    # Create buttons in a 2-column grid
    for i, (text, cmd) in enumerate(options):
        row = i // 2
        col = i % 2
        btn = tk.Button(
            option_frame,
            text=text,
            font=btn_font,
            width=25,
            height=2,
            relief='flat',
            bg='white',
            activebackground='#e0e0e0',
            bd=0,
            highlightthickness=0,
            command=cmd
        )
        btn.grid(row=row, column=col, padx=15, pady=15)

    # Center the grid columns
    option_frame.grid_columnconfigure(0, weight=1)
    option_frame.grid_columnconfigure(1, weight=1)
