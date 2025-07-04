import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import tkinter as tk
from tkinter import ttk
import db_connect
from datetime import date, timedelta

def show_monthly_balance_sheet(app):
    for widget in app.root.winfo_children():
        widget.destroy()
    app.set_background()
    app.get_responsive_fonts()
    label_font = app.fonts['label']
    button_font = app.fonts['button']

    tk.Button(app.root, text="← Go Back", command=app.show_view_transactions_menu, font=button_font).pack(anchor='w', padx=10, pady=10)
    tk.Label(app.root, text="Monthly Balance Sheet", font=label_font, bg="white").pack(pady=20)

    table_frame = tk.Frame(app.root, bg='white')
    table_frame.pack(fill='both', expand=True, padx=30, pady=10)

    columns = ("Particulars", "Balance")
    tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor='center', width=200)

    try:
        today = date.today()
        first_of_month = today.replace(day=1)
        end_last_month = first_of_month - timedelta(days=1)

        conn = db_connect.get_connection()
        cursor = conn.cursor(dictionary=True)

        # --- Main Fund / Bank Balance ---
        query_bank = '''
            SELECT
                (SELECT COALESCE(SUM(amount), 0) FROM journal_entries WHERE entry_type = 'Fund' AND entry_id NOT LIKE 'C%%' AND entry_date <= %s) - 
                (SELECT COALESCE(SUM(amount), 0) FROM journal_entries WHERE entry_type = 'Bank' AND entry_id NOT LIKE 'C%%' AND entry_date <= %s)
                AS total
        '''
        cursor.execute(query_bank, (end_last_month, end_last_month))
        main_fund_bal = cursor.fetchone()['total'] or 0

        # --- FD, Property, Sundry, Fund, and Cash Balances ---
        def get_total_for_asset(asset_column):
            query = f"""
                SELECT COALESCE(SUM({asset_column}), 0) AS total 
                FROM journal_entries 
                WHERE entry_id LIKE 'C%%' 
                  AND {asset_column} IS NOT NULL 
                  AND entry_date <= %s
            """
            cursor.execute(query, (end_last_month,))
            return cursor.fetchone()['total'] or 0

        total_fd = get_total_for_asset('fd')
        total_prop = get_total_for_asset('property')
        total_sundry = get_total_for_asset('sundry')
        total_cash = get_total_for_asset('cash')

        # --- Fund Balance (Receipts - Payments from counter-entries) ---
        query_fund = """
            SELECT 
                (SELECT COALESCE(SUM(fund), 0) FROM journal_entries WHERE entry_id LIKE 'CERV%%' AND entry_date <= %s) -
                (SELECT COALESCE(SUM(fund), 0) FROM journal_entries WHERE entry_id LIKE 'CEPV%%' AND entry_date <= %s)
            AS total_fund
        """
        cursor.execute(query_fund, (end_last_month, end_last_month))
        total_fund_result = cursor.fetchone()
        total_fund = total_fund_result['total_fund'] if total_fund_result and total_fund_result['total_fund'] is not None else 0

        cursor.close()
        conn.close()

        # --- Populate the Treeview ---
        balances = {
            "Bank Balance": main_fund_bal,
            "FD Balance": total_fd,
            "Property Balance": total_prop,
            "Sundry Balance": total_sundry,
            "Fund Balance": total_fund,
            "Cash Balance": total_cash
        }

        for particular, balance in balances.items():
            tree.insert('', 'end', values=(particular, f"{balance:,.2f}"))

    except Exception as e:
        from tkinter import messagebox
        messagebox.showerror("Database Error", f"Failed to fetch balance sheet data: {e}")

    tree.pack(side='left', fill='both', expand=True)
    vsb = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=vsb.set)
    vsb.pack(side='right', fill='y')
