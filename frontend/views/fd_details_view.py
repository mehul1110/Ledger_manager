import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import tkinter as tk
from tkcalendar import DateEntry
import db_connect
import tkinter.ttk as ttk
import csv
import openpyxl
from tkinter import filedialog, messagebox
import utils

def sort_column(tree, col, reverse):
    # Helper function to convert to float for sorting, fallback to string
    def to_float_or_str(val):
        try:
            return float(val)
        except (ValueError, TypeError):
            return str(val)

    l = [(to_float_or_str(tree.set(k, col)), k) for k in tree.get_children('')]
    l.sort(key=lambda t: t[0], reverse=reverse)

    for index, (val, k) in enumerate(l):
        tree.move(k, '', index)

    tree.heading(col, text=col, command=lambda: sort_column(tree, col, not reverse))

def show_fd_details_view(app):
    for widget in app.root.winfo_children():
        widget.destroy()
    app.set_background()
    app.get_responsive_fonts()
    label_font = app.fonts['label']
    button_font = app.fonts['button']

    tk.Button(app.root, text="← Go Back", command=app.show_view_transactions_menu, font=button_font).pack(anchor='w', padx=10, pady=10)
    
    tk.Label(app.root, text="Fixed Deposit Details", font=label_font, bg="white").pack(pady=20)

    # Filters Frame
    filters_frame = tk.Frame(app.root, bg='white')
    filters_frame.pack(pady=10)

    tk.Label(filters_frame, text="Start Date:", font=label_font, bg='white').grid(row=0, column=0, padx=5)
    start_date_var = tk.StringVar(value='')
    start_date_entry = DateEntry(filters_frame, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern='dd-mm-yyyy', textvariable=start_date_var)
    start_date_entry.grid(row=0, column=1, padx=5)

    tk.Label(filters_frame, text="End Date:", font=label_font, bg='white').grid(row=0, column=2, padx=5)
    end_date_var = tk.StringVar(value='')
    end_date_entry = DateEntry(filters_frame, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern='dd-mm-yyyy', textvariable=end_date_var)
    end_date_entry.grid(row=0, column=3, padx=5)

    conn = db_connect.get_connection()
    cursor = conn.cursor()

    # Status Filter
    tk.Label(filters_frame, text="Status:", font=label_font, bg='white').grid(row=0, column=4, padx=5)
    cursor.execute("SELECT DISTINCT status FROM fd_details ORDER BY status")
    statuses = [row[0] for row in cursor.fetchall()]
    status_var = tk.StringVar(value="All")
    status_dropdown = tk.OptionMenu(filters_frame, status_var, "All", *statuses)
    status_dropdown.grid(row=0, column=5, padx=5)

    table_frame = tk.Frame(app.root, bg='', highlightthickness=0, bd=0)
    table_frame.pack(fill='both', expand=True, padx=30, pady=10)

    columns = [
        "Payment ID", "Bank Account", "Amount", "Duration", "Interest Rate",
        "Narration", "FD Date", "Maturity Date", "Status", "Maturity Amount"
    ]
    tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
    
    for col in columns:
        tree.heading(col, text=col, command=lambda c=col: sort_column(tree, c, False))
        if col in ["Amount", "Interest Rate", "Maturity Amount"]:
            tree.column(col, anchor='e', width=120)
        elif col in ["Payment ID", "Duration", "FD Date", "Maturity Date"]:
            tree.column(col, anchor='center', width=100)
        else:
            tree.column(col, anchor='w', width=150)

    def is_valid_date(date_str):
        # Accepts only if user has picked a date (not empty, not today's date)
        return bool(date_str and date_str.strip())

    def apply_filters():
        # Clear existing rows
        for i in tree.get_children():
            tree.delete(i)
        # Construct query - select only the columns we want to display (exclude internal id)
        query = (
            "SELECT payment_id, bank_account, amount, duration, interest_rate, "
            "narration, fd_date, maturity_date, status, maturity_amount "
            "FROM fd_details WHERE 1=1"
        )
        # Only apply date filter if user selects a date and it is not today's date
        today_str = utils.get_today_str()  # You should implement this in utils.py to return today's date in dd-mm-yyyy
        start_date = start_date_entry.get().strip()
        end_date = end_date_entry.get().strip()
        if start_date and start_date != today_str:
            date_from = utils.parse_date(start_date)
            if date_from:
                query += f" AND fd_date >= '{date_from.strftime('%Y-%m-%d')}'"
        if end_date and end_date != today_str:
            date_to = utils.parse_date(end_date)
            if date_to:
                query += f" AND fd_date <= '{date_to.strftime('%Y-%m-%d')}'"
        if status_var.get() != "All":
            query += f" AND status = '{status_var.get()}'"
        query += " ORDER BY payment_id ASC"
        # Debug: print query and params
        print(f"[DEBUG] fd_details_view executing: {query}")
        # Fetch data with fresh connection
        try:
            conn_data = db_connect.get_connection()
            cursor_data = conn_data.cursor()
            cursor_data.execute(query)
            rows = cursor_data.fetchall()
            for row in rows:
                # Format the data properly
                formatted_row = list(row)
                # Format amount with 2 decimal places if it exists (index 2)
                if formatted_row[2] is not None:
                    formatted_row[2] = f"{float(formatted_row[2]):.2f}"
                # Format interest rate with 2 decimal places if it exists (index 4)
                if formatted_row[4] is not None:
                    formatted_row[4] = f"{float(formatted_row[4]):.2f}%"
                # Format maturity amount with 2 decimal places if it exists (index 9)
                if formatted_row[9] is not None:
                    formatted_row[9] = f"{float(formatted_row[9]):.2f}"
                tree.insert('', 'end', values=formatted_row)
            cursor_data.close()
            conn_data.close()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    def clear_filters():
        start_date_entry.set_date('')
        end_date_entry.set_date('')
        status_var.set("All")
        apply_filters()

    tk.Button(filters_frame, text="Filter", command=apply_filters, font=button_font).grid(row=0, column=6, padx=5)
    tk.Button(filters_frame, text="Clear", command=clear_filters, font=button_font).grid(row=0, column=7, padx=5)

    apply_filters() # Initial data load: show all entries

    vsb = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=vsb.set)
    tree.pack(side='left', fill='both', expand=True)
    vsb.pack(side='right', fill='y')

    def export_to_csv():
        file_path = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV files', '*.csv')], title='Save as')
        if not file_path:
            return
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(columns)
                for row_id in tree.get_children():
                    writer.writerow(tree.item(row_id)['values'])
            messagebox.showinfo('Export Successful', f'FD details exported to {file_path}')
        except Exception as e:
            messagebox.showerror('Export Failed', f'Error: {e}')
            
    export_btn = tk.Button(app.root, text="Export as CSV", font=button_font, command=export_to_csv, bg="#e0e0e0")
    export_btn.pack(pady=(0, 10))

    cursor.close()
    conn.close()
