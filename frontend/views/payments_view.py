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
import utils  # <-- add this import

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

def show_payments_view(app):
    for widget in app.root.winfo_children():
        widget.destroy()
    app.set_background()
    app.get_responsive_fonts()
    label_font = app.fonts['label']
    button_font = app.fonts['button']
    tk.Button(app.root, text="← Go Back", command=app.show_view_transactions_menu, font=button_font).pack(anchor='w', padx=10, pady=10)
    tk.Label(app.root, text="Payments", font=label_font, bg="white").pack(pady=20)

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

    # Account and Narration Filters using fresh connection
    try:
        conn_filters = db_connect.get_connection()
        cursor_filters = conn_filters.cursor()
        # Account Filter
        tk.Label(filters_frame, text="Account:", font=label_font, bg='white').grid(row=0, column=4, padx=5)
        cursor_filters.execute("SELECT DISTINCT account_name FROM payments ORDER BY account_name")
        accounts = [row[0] for row in cursor_filters.fetchall()]
        account_var = tk.StringVar(value="All")
        tk.OptionMenu(filters_frame, account_var, "All", *accounts).grid(row=0, column=5, padx=5)
        # Narration Filter
        tk.Label(filters_frame, text="Narration:", font=label_font, bg='white').grid(row=0, column=6, padx=5)
        cursor_filters.execute("SELECT DISTINCT narration FROM payments ORDER BY narration")
        narrations = [row[0] for row in cursor_filters.fetchall()]
        narration_var = tk.StringVar(value="All")
        tk.OptionMenu(filters_frame, narration_var, "All", *narrations).grid(row=0, column=7, padx=5)
    except Exception as e:
        messagebox.showerror('Database Error', f'Failed to load filter options: {e}')
    finally:
        cursor_filters.close()
        conn_filters.close()

    table_frame = tk.Frame(app.root, bg='', highlightthickness=0, bd=0)
    table_frame.pack(fill='both', expand=True, padx=30, pady=10)
    
    columns = ["Payment ID", "Date", "Account Name", "Amount", "Mode", "Narration", "Remarks"]
    tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
    for col in columns:
        tree.heading(col, text=col, command=lambda c=col: sort_column(tree, c, False))
        tree.column(col, anchor='center', width=120)

    def is_valid_date(date_str):
        # Accepts only if user has picked a date (not empty, not today's date)
        return bool(date_str and date_str.strip())

    def apply_filters():
        # Clear existing rows
        for i in tree.get_children():
            tree.delete(i)
        # Construct query
        query = (
            "SELECT payment_id, account_name, amount, mop, narration, remarks, date "
            "FROM payments WHERE 1=1"
        )
        # Only apply date filter if user selects a date and it is not today's date
        today_str = utils.get_today_str()  # You should implement this in utils.py to return today's date in dd-mm-yyyy
        start_date = start_date_entry.get().strip()
        end_date = end_date_entry.get().strip()
        if start_date and start_date != today_str:
            date_from = utils.parse_date(start_date)
            if date_from:
                query += f" AND date >= '{date_from.strftime('%Y-%m-%d')}'"
        if end_date and end_date != today_str:
            date_to = utils.parse_date(end_date)
            if date_to:
                query += f" AND date <= '{date_to.strftime('%Y-%m-%d')}'"
        if account_var.get() != "All":
            query += f" AND account_name = '{account_var.get()}'"
        if narration_var.get() != "All":
            query += f" AND narration = '{narration_var.get()}'"
        query += " ORDER BY payment_id ASC"
        print(f"[DEBUG] payments_view executing: {query}")
        try:
            conn_data = db_connect.get_connection()
            cursor_data = conn_data.cursor()
            cursor_data.execute(query)
            rows = cursor_data.fetchall()
            for row_data in rows:
                row_list = list(row_data)
                # Reorder to move date to the second position
                entry_date = row_list.pop(6) # date is the last column
                row_list.insert(1, entry_date)
                tree.insert('', 'end', values=row_list)
        except Exception as e:
            messagebox.showerror('Database Error', f'Failed to fetch payments: {e}')
        finally:
            if 'conn_data' in locals() and conn_data.is_connected():
                cursor_data.close()
                conn_data.close()

    def clear_filters():
        start_date_entry.set_date(None)
        end_date_entry.set_date(None)
        account_var.set("All")
        narration_var.set("All")
        apply_filters()

    tk.Button(filters_frame, text="Filter", command=apply_filters, font=button_font).grid(row=0, column=8, padx=5)
    tk.Button(filters_frame, text="Clear", command=clear_filters, font=button_font).grid(row=0, column=9, padx=5)

    vsb = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=vsb.set)
    tree.pack(side='left', fill='both', expand=True)
    vsb.pack(side='right', fill='y')

    def export_to_csv():
        file_path = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV files', '*.csv')], title='Save as')
        if not file_path:
            return
        try:
            from datetime import date, timedelta
            today = date.today()
            first_of_month = today.replace(day=1)
            end_last_month = first_of_month - timedelta(days=1)

            # Fetch brought forward balances for specific categories
            conn = db_connect.get_connection()
            cursor = conn.cursor()

            # --- Main Fund / Bank Balance ---
            query_bank = '''
                SELECT
                    COALESCE(SUM(CASE WHEN entry_type = 'Bank' THEN amount ELSE 0 END), 0) -
                    COALESCE(SUM(CASE WHEN entry_type = 'Fund' THEN amount ELSE 0 END), 0)
                    AS total
                FROM journal_entries
                WHERE 
                    account_name = 'main fund' 
                    AND entry_id LIKE 'C%%'
                    AND entry_date <= %s
            '''
            cursor.execute(query_bank, (end_last_month,))
            main_fund_bal = cursor.fetchone()[0] or 0

            # --- FD, Property, and Sundry Balances ---
            query_fd = """
                SELECT COALESCE(SUM(fd), 0) AS total 
                FROM journal_entries 
                WHERE entry_type = 'Fund' 
                  AND fd IS NOT NULL 
                  AND entry_date <= %s
            """
            cursor.execute(query_fd, (end_last_month,))
            total_fd = cursor.fetchone()[0] or 0

            query_prop = """
                SELECT COALESCE(SUM(property), 0) AS total 
                FROM journal_entries 
                WHERE entry_type = 'Fund' 
                  AND property IS NOT NULL 
                  AND entry_date <= %s
            """
            cursor.execute(query_prop, (end_last_month,))
            total_prop = cursor.fetchone()[0] or 0

            query_sundry = """
                SELECT COALESCE(SUM(sundry), 0) AS total 
                FROM journal_entries 
                WHERE entry_type = 'Fund' 
                  AND sundry IS NOT NULL 
                  AND entry_date <= %s
            """
            cursor.execute(query_sundry, (end_last_month,))
            total_sundry = cursor.fetchone()[0] or 0

            cursor.close()
            conn.close()

            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)

                # Write custom first line with brought forward balances
                custom_line = [
                    f"Main Fund: {main_fund_bal:,.2f}",
                    f"FD: {total_fd:,.2f}",
                    f"Property: {total_prop:,.2f}",
                    f"Sundry: {total_sundry:,.2f}"
                ]
                writer.writerow(["Brought Forward Balances:"] + custom_line)

                # Write column headers
                writer.writerow(columns)

                # Write data rows
                for row_id in tree.get_children():
                    writer.writerow(tree.item(row_id)['values'])

            messagebox.showinfo('Export Successful', f'Payments exported to {file_path}')
        except Exception as e:
            messagebox.showerror('Export Failed', f'Error: {e}')
    export_btn = tk.Button(app.root, text="Export as CSV", font=button_font, command=export_to_csv, bg="#e0e0e0")
    export_btn.pack(pady=(0, 10))

    apply_filters()  # Initial data load: show all entries
