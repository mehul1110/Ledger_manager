import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import tkinter as tk
from tkcalendar import DateEntry
import db_connect
import tkinter.ttk as ttk
from tkinter import messagebox
from datetime import datetime


def show_comparison_view(app):
    for widget in app.root.winfo_children():
        widget.destroy()
    app.set_background()
    app.get_responsive_fonts()
    label_font = app.fonts['label']
    button_font = app.fonts['button']

    # Header and Go Back
    tk.Button(app.root, text="← Go Back", command=app.show_view_transactions_menu, font=button_font).pack(anchor='w', padx=10, pady=10)
    tk.Label(app.root, text="Monthly Balance Comparison", font=label_font, bg="white").pack(pady=20)

    # Selection Frame
    select_frame = tk.Frame(app.root, bg='white')
    select_frame.pack(pady=10)

    tk.Label(select_frame, text="Month 1 (MM-YYYY):", font=label_font, bg='white').grid(row=0, column=0, padx=5)
    month1_var = tk.StringVar(value="06-2025")  # Default example
    month1_entry = tk.Entry(select_frame, textvariable=month1_var, width=12, font=label_font)
    month1_entry.grid(row=0, column=1, padx=5)

    tk.Label(select_frame, text="Month 2 (MM-YYYY):", font=label_font, bg='white').grid(row=0, column=2, padx=5)
    month2_var = tk.StringVar(value="07-2025")  # Default example
    month2_entry = tk.Entry(select_frame, textvariable=month2_var, width=12, font=label_font)
    month2_entry.grid(row=0, column=3, padx=5)

    compare_button = tk.Button(select_frame, text="Compare", font=button_font, command=lambda: apply_comparison(), bg="#4CAF50", fg="white")
    compare_button.grid(row=0, column=4, padx=10)

    # Table Frame
    table_frame = tk.Frame(app.root, bg='white')
    table_frame.pack(fill='both', expand=True, padx=30, pady=10)

    columns = ["Month", "Opening", "Closing"]
    tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=10)
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor='center', width=150)
    tree.pack(side='left', fill='both', expand=True)

    scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side='right', fill='y')

    def apply_comparison():
        # Clear previous results
        for i in tree.get_children():
            tree.delete(i)

        # Parse selected dates to YYYY-MM
        try:
            # month-year format parsing, defaults day to 1
            d1 = datetime.strptime(month1_var.get(), '%m-%Y')
            d2 = datetime.strptime(month2_var.get(), '%m-%Y')
            m1 = f"{d1.year:04d}-{d1.month:02d}"
            m2 = f"{d2.year:04d}-{d2.month:02d}"
        except Exception as e:
            messagebox.showerror('Invalid Date', 'Please select valid months in MM-YYYY format.')
            return

        # Fetch balances
        try:
            conn = db_connect.get_connection()
            cursor = conn.cursor()
            query = (
                "SELECT month, opening, closing FROM monthly_main_fund_balance "
                "WHERE month IN (%s, %s) ORDER BY month ASC"
            )
            cursor.execute(query, (m1, m2))
            rows = cursor.fetchall()
            if not rows:
                messagebox.showinfo('No Data', 'No balance data found for the selected months.')
                return
            for row in rows:
                tree.insert('', 'end', values=row)
        except Exception as e:
            messagebox.showerror('Database Error', f'Failed to fetch comparison: {e}')
        finally:
            cursor.close()
            conn.close()
