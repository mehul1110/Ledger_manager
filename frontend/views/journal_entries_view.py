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

def show_journal_entries_view(app):
    for widget in app.root.winfo_children():
        widget.destroy()
    app.set_background()
    app.get_responsive_fonts()
    label_font = app.fonts['label']
    button_font = app.fonts['button']
    tk.Button(app.root, text="← Go Back", command=app.show_view_transactions_menu, font=button_font).pack(anchor='w', padx=10, pady=10)
    tk.Label(app.root, text="Journal Entries", font=label_font, bg="white").pack(pady=20)

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
        cursor_filters.execute("SELECT DISTINCT account_name FROM journal_entries ORDER BY account_name")
        accounts = [row[0] for row in cursor_filters.fetchall()]
        account_var = tk.StringVar(value="All")
        tk.OptionMenu(filters_frame, account_var, "All", *accounts).grid(row=0, column=5, padx=5)
        # Narration Filter
        tk.Label(filters_frame, text="Narration:", font=label_font, bg='white').grid(row=0, column=6, padx=5)
        cursor_filters.execute("SELECT DISTINCT narration FROM journal_entries ORDER BY narration")
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

    # Define internal column identifiers and their display names
    column_map = {
        "entry_id": "Voucher No.",
        "entry_date": "Date",
        "account_name": "Particulars",
        "narration": "Narration",
        "mop": "Mode of Payment",
        "amount": "Bank",
        "fd": "FD",
        "sundry": "Sundry Dr",
        "property": "Property",
        "fund": "EME Journal Fund",
        "cash": "Cash"
    }
    
    columns = list(column_map.keys()) # These are the internal identifiers
    display_names = list(column_map.values()) # These are for display

    tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
    for col_id, display_name in column_map.items():
        tree.heading(col_id, text=display_name, command=lambda c=col_id: sort_column(tree, c, False))
        tree.column(col_id, anchor='center', width=120)

    def is_valid_date(date_str):
        # Accepts only if user has picked a date (not empty, not today's date)
        return bool(date_str and date_str.strip())

    def apply_filters():
        # Clear existing rows
        for i in tree.get_children():
            tree.delete(i)
        # Construct query
        query = (
            "SELECT entry_id, entry_date, account_name, entry_type, amount, narration, mop, fd, sundry, property, fund, cash "
            "FROM journal_entries WHERE 1=1"
        )
        # Only apply date filter if user selects a date and it is not today's date
        today_str = utils.get_today_str()  # Should return today's date in dd-mm-yyyy
        start_date = start_date_entry.get().strip()
        end_date = end_date_entry.get().strip()
        if start_date and start_date != today_str:
            date_from = utils.parse_date(start_date)
            if date_from:
                query += f" AND entry_date >= '{date_from.strftime('%Y-%m-%d')}'"
        if end_date and end_date != today_str:
            date_to = utils.parse_date(end_date)
            if date_to:
                query += f" AND entry_date <= '{date_to.strftime('%Y-%m-%d')}'"
        if account_var.get() != "All":
            query += f" AND account_name = '{account_var.get()}'"
        if narration_var.get() != "All":
            query += f" AND narration = '{narration_var.get()}'"
        query += " ORDER BY id ASC"
        print(f"[DEBUG] journal_entries_view executing: {query}")
        try:
            conn_data = db_connect.get_connection()
            cursor_data = conn_data.cursor()
            cursor_data.execute(query)
            rows = cursor_data.fetchall()
            print(f"[DEBUG] journal_entries_view fetched {len(rows)} rows")
            for row_data in rows:
                # Correctly map fetched data to variables
                (entry_id, entry_date, account_name, entry_type, amount, 
                 narration, mop, fd, sundry, prop, fund_val, cash_val) = row_data

                # For display, format None values as empty strings
                display_amount = f"{amount:.2f}" if amount is not None else ""
                display_fd = f"{fd:.2f}" if fd is not None else ""
                display_sundry = f"{sundry:.2f}" if sundry is not None else ""
                display_prop = f"{prop:.2f}" if prop is not None else ""
                display_fund = f"{fund_val:.2f}" if fund_val is not None else ""
                display_cash = f"{cash_val:.2f}" if cash_val is not None else ""

                # Assemble the final row for display in the correct order
                final_row = [
                    entry_id,
                    entry_date.strftime('%d-%m-%Y') if entry_date else '',
                    account_name,
                    narration,
                    mop,
                    display_amount,
                    display_fd,
                    display_sundry,
                    display_prop,
                    display_fund,
                    display_cash
                ]
                
                tree.insert('', 'end', values=final_row)
        except Exception as e:
            messagebox.showerror('Database Error', f'Failed to fetch journal entries: {e}')
        finally:
            cursor_data.close()
            conn_data.close()

    def clear_filters():
        start_date_entry.set_date('')
        end_date_entry.set_date('')
        account_var.set("All")
        narration_var.set("All")
        apply_filters()

    tk.Button(filters_frame, text="Filter", command=apply_filters, font=button_font).grid(row=0, column=8, padx=5)
    tk.Button(filters_frame, text="Clear", command=clear_filters, font=button_font).grid(row=0, column=9, padx=5)

    # --- End-of-Last-Month Balances Panel ---
    balances_frame = tk.Frame(filters_frame, bg='white')
    balances_frame.grid(row=1, column=0, columnspan=10, pady=(10,0), sticky='w')
    balances_label = tk.Label(balances_frame,
                              text="Bank: -- | FD: -- | Property: -- | Sundry: -- | Cash: --",
                              font=label_font, bg='white')
    balances_label.pack()

    def compute_balances():
        from datetime import date, timedelta
        today = date.today()
        first_of_month = today.replace(day=1)
        end_last_month = first_of_month - timedelta(days=1)
        conn_bal = db_connect.get_connection()
        cur_bal = conn_bal.cursor(dictionary=True)

        def get_balance_for(column_name):
            # For 'Bank', we sum receipts and subtract payments from the 'amount' column.
            if column_name == 'amount':
                query = """
                    SELECT 
                        COALESCE(SUM(CASE WHEN entry_type IN ('Fund', 'System') THEN amount ELSE -amount END), 0) as total
                    FROM journal_entries 
                    WHERE entry_type IN ('Bank', 'Fund', 'System') AND amount IS NOT NULL AND entry_date <= %s
                """
            # For 'Fund', we need to consider the entry type to add or subtract.
            elif column_name == 'fund':
                query = """
                    SELECT
                        COALESCE(SUM(CASE WHEN entry_type IN ('Bank', 'System') THEN fund ELSE -fund END), 0) as total
                    FROM journal_entries
                    WHERE fund IS NOT NULL AND entry_date <= %s
                """
            # For 'Cash', handle specific narrations for addition and subtraction.
            elif column_name == 'cash':
                query = """
                    SELECT 
                        COALESCE(SUM(CASE 
                            WHEN narration IN ('Cash Withdrawal', 'Petty Cash Withdrawal') THEN cash 
                            WHEN narration = 'Petty Cash Expenditure' THEN -cash 
                            ELSE 0 END), 0) as total
                    FROM journal_entries
                    WHERE cash IS NOT NULL AND entry_date <= %s
                """
            # For all other columns (assets), we just sum the values.
            else:
                query = f"""
                    SELECT COALESCE(SUM({column_name}), 0) as total 
                    FROM journal_entries 
                    WHERE {column_name} IS NOT NULL AND entry_date <= %s
                """
            cur_bal.execute(query, (end_last_month,))
            result = cur_bal.fetchone()
            return result['total'] if result else 0

        main_fund_bal = get_balance_for('amount')
        total_fd = get_balance_for('fd')
        total_prop = get_balance_for('property')
        total_sundry = get_balance_for('sundry')
        total_fund = get_balance_for('fund')
        total_cash = get_balance_for('cash')
        
        cur_bal.close()
        conn_bal.close()
        
        # Update single balances label
        balances_label.config(
            text=(f"Bank: {main_fund_bal:,.2f} | "
                  f"FD: {total_fd:,.2f} | "
                  f"Property: {total_prop:,.2f} | "
                  f"Sundry: {total_sundry:,.2f} | "
                  f"Fund: {total_fund:,.2f} | "
                  f"Cash: {total_cash:,.2f}"))

    # Initial balance computation
    compute_balances()

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

            # Re-use the balance computation logic for consistency
            conn = db_connect.get_connection()
            cursor = conn.cursor(dictionary=True)

            def get_balance_for_export(column_name):
                if column_name == 'amount':
                    query = """
                        SELECT 
                            COALESCE(SUM(CASE WHEN entry_type IN ('Fund', 'System') THEN amount ELSE -amount END), 0) as total
                        FROM journal_entries 
                        WHERE entry_type IN ('Bank', 'Fund', 'System') AND amount IS NOT NULL AND entry_date <= %s
                    """
                elif column_name == 'fund':
                    query = """
                        SELECT
                            COALESCE(SUM(CASE WHEN entry_type IN ('Bank', 'System') THEN fund ELSE -fund END), 0) as total
                        FROM journal_entries
                        WHERE fund IS NOT NULL AND entry_date <= %s
                    """
                # For all other columns (assets), we just sum the values.
                else:
                    query = f"""
                        SELECT COALESCE(SUM({column_name}), 0) as total 
                        FROM journal_entries 
                        WHERE {column_name} IS NOT NULL AND entry_date <= %s
                    """
                cursor.execute(query, (end_last_month,))
                result = cursor.fetchone()
                return result['total'] if result else 0

            main_fund_bal = get_balance_for_export('amount')
            total_fd = get_balance_for_export('fd')
            total_prop = get_balance_for_export('property')
            total_sundry = get_balance_for_export('sundry')
            total_fund = get_balance_for_export('fund')
            total_cash = get_balance_for_export('cash')

            cursor.close()
            conn.close()

            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)

                # Write custom first line with brought forward balances
                custom_line = [
                    f"Bank: {main_fund_bal:,.2f}",
                    f"FD: {total_fd:,.2f}",
                    f"Property: {total_prop:,.2f}",
                    f"Sundry: {total_sundry:,.2f}",
                    f"Fund: {total_fund:,.2f}",
                    f"Cash: {total_cash:,.2f}"
                ]
                writer.writerow(["Brought Forward Balances:"] + custom_line)

                # Write column headers
                writer.writerow(display_names)

                # Write data rows
                for row_id in tree.get_children():
                    writer.writerow(tree.item(row_id)['values'])

            messagebox.showinfo('Export Successful', f'Journal entries exported to {file_path}')
        except Exception as e:
            messagebox.showerror('Export Failed', f'Error: {e}')
    export_btn = tk.Button(app.root, text="Export as CSV", font=button_font, command=export_to_csv, bg="#e0e0e0")
    export_btn.pack(pady=(0, 10))

    apply_filters()  # Initial data load: show all entries
