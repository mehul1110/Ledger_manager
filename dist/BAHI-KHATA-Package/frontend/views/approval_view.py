import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
import db_connect
from transaction_approver import process_pending_transaction

def show_approval_view(app, on_success_callback=None):
    for widget in app.root.winfo_children():
        widget.destroy()
    app.set_background()
    app.get_responsive_fonts()
    label_font = app.fonts['label']
    button_font = app.fonts['button']

    tk.Button(app.root, text="← Go Back", command=app.show_main_menu, font=button_font).pack(anchor='w', padx=10, pady=10)
    tk.Label(app.root, text="Approve Transactions", font=label_font, bg="white").pack(pady=20)

    table_frame = tk.Frame(app.root, bg='white')
    table_frame.pack(fill='both', expand=True, padx=20, pady=10)

    columns = ["ID", "Type", "Date", "Account", "Amount", "Narration", "MOP", "Remarks"]
    tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor='w', width=120)
    tree.column("ID", width=40, anchor='center')
    tree.column("Amount", width=80, anchor='e')

    def populate_tree():
        for i in tree.get_children():
            tree.delete(i)
        try:
            conn = db_connect.get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id, transaction_type, transaction_date, account_name, amount, narration, mop, remarks FROM pending_transactions ORDER BY created_at DESC")
            rows = cursor.fetchall()
            for row in rows:
                tree.insert('' , 'end', values=list(row.values()))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch pending transactions: {e}")
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    def handle_selection(action):
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a transaction to " + action)
            return
        
        pending_id = tree.item(selected_item, "values")[0]

        def refresh_and_reload():
            populate_tree() # Refresh the approval list
            app.update_pending_count() # Refresh the sidebar count
            if on_success_callback:
                on_success_callback()

        process_pending_transaction(pending_id, action, success_callback=refresh_and_reload)

    button_frame = tk.Frame(app.root, bg='white')
    button_frame.pack(pady=10)

    approve_button = tk.Button(button_frame, text="Approve", font=button_font, command=lambda: handle_selection('approve'), bg="#4CAF50", fg="white")
    approve_button.pack(side='left', padx=10)

    reject_button = tk.Button(button_frame, text="Reject", font=button_font, command=lambda: handle_selection('reject'), bg="#f44336", fg="white")
    reject_button.pack(side='left', padx=10)

    refresh_button = tk.Button(button_frame, text="Refresh", font=button_font, command=populate_tree)
    refresh_button.pack(side='left', padx=10)

    vsb = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=vsb.set)
    tree.pack(side='left', fill='both', expand=True)
    vsb.pack(side='right', fill='y')

    populate_tree()
