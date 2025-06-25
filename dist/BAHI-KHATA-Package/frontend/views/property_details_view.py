import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import tkinter as tk
from tkcalendar import DateEntry
import db_connect
import tkinter.ttk as ttk
import csv
from tkinter import filedialog, messagebox
import utils

def sort_column(tree, col, reverse):
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

def show_property_details_view(app):
    for widget in app.root.winfo_children():
        widget.destroy()
    app.set_background()
    
    app.get_responsive_fonts()
    label_font = app.fonts['label']
    button_font = app.fonts['button']

    tk.Button(app.root, text="← Go Back", command=app.show_view_transactions_menu, font=button_font).pack(anchor='w', padx=10, pady=10)
    
    tk.Label(app.root, text="Property Details", font=label_font, bg="white").pack(pady=20)

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

    # Type Filter
    tk.Label(filters_frame, text="Type:", font=label_font, bg='white').grid(row=0, column=4, padx=5)
    cursor.execute("SELECT DISTINCT `type` FROM property_details ORDER BY `type`")
    types = [row[0] for row in cursor.fetchall()]
    type_var = tk.StringVar(value="All")
    type_dropdown = tk.OptionMenu(filters_frame, type_var, "All", *types)
    type_dropdown.grid(row=0, column=5, padx=5)

    table_frame = tk.Frame(app.root, bg='', highlightthickness=0, bd=0)
    table_frame.pack(fill='both', expand=True, padx=30, pady=10)

    columns = [
        "Payment ID", "Item Name", "Description", "Type", "Value",
        "Purchase Date", "Depreciation Rate"
    ]
    tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
    
    for col in columns:
        tree.heading(col, text=col, command=lambda c=col: sort_column(tree, c, False))
        if col in ["Value", "Depreciation Rate"]:
            tree.column(col, anchor='e', width=120)
        elif col in ["Purchase Date"]:
            tree.column(col, anchor='center', width=120)
        else:
            tree.column(col, anchor='w', width=150)

    def is_valid_date(date_str):
        # Accepts only if user has picked a date (not empty, not today's date)
        return bool(date_str and date_str.strip())

    def apply_filters():
        # Clear existing rows
        for i in tree.get_children():
            tree.delete(i)
        # Construct query
        query = (
            "SELECT * FROM property_details WHERE 1=1"
        )
        # Only apply date filter if user selects a date and it is not today's date
        today_str = utils.get_today_str()  # You should implement this in utils.py to return today's date in dd-mm-yyyy
        start_date = start_date_entry.get().strip()
        end_date = end_date_entry.get().strip()
        if start_date and start_date != today_str:
            date_from = utils.parse_date(start_date)
            if date_from:
                query += f" AND purchase_date >= '{date_from.strftime('%Y-%m-%d')}'"
        if end_date and end_date != today_str:
            date_to = utils.parse_date(end_date)
            if date_to:
                query += f" AND purchase_date <= '{date_to.strftime('%Y-%m-%d')}'"
        if type_var.get() != "All":
            query += f" AND type = '{type_var.get()}'"
        query += " ORDER BY id ASC"
        print(f"[DEBUG] property_details_view executing: {query}")
        try:
            conn_data = db_connect.get_connection()
            cursor_data = conn_data.cursor()
            cursor_data.execute(query)
            rows = cursor_data.fetchall()
            for row in rows:
                tree.insert('', 'end', values=row)
            cursor_data.close()
            conn_data.close()
        except Exception as e:
            print(f"[ERROR] Failed to fetch data: {e}")

    def clear_filters():
        start_date_entry.set_date('')
        end_date_entry.set_date('')
        type_var.set("All")
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
            messagebox.showinfo('Export Successful', f'Property details exported to {file_path}')
        except Exception as e:
            messagebox.showerror('Export Failed', f'Error: {e}')
            
    export_btn = tk.Button(app.root, text="Export as CSV", font=button_font, command=export_to_csv, bg="#e0e0e0")
    export_btn.pack(pady=(0, 10))

    cursor.close()
    conn.close()
