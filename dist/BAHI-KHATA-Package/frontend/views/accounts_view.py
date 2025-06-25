import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import tkinter as tk
import db_connect
import tkinter.ttk as ttk
from tkinter import messagebox
from account_utils import delete_account

def sort_column(tree, col, reverse):
    l = [(tree.set(k, col), k) for k in tree.get_children('')]
    l.sort(reverse=reverse)

    for index, (val, k) in enumerate(l):
        tree.move(k, '', index)

    tree.heading(col, command=lambda: sort_column(tree, col, not reverse))

def show_accounts_view(app):
    for widget in app.root.winfo_children():
        widget.destroy()
    app.set_background()
    app.get_responsive_fonts()
    label_font = app.fonts['label']
    button_font = app.fonts['button']
    tk.Button(app.root, text="← Go Back", command=app.show_view_transactions_menu, font=button_font).pack(anchor='w', padx=10, pady=10)
    tk.Label(app.root, text="Accounts", font=label_font, bg="white").pack(pady=20)
    conn = db_connect.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT account_name, account_type FROM accounts ORDER BY account_name ASC")
    rows = cursor.fetchall()
    columns = ["Account Name", "Account Type"]
    table_frame = tk.Frame(app.root, bg='', highlightthickness=0, bd=0)
    table_frame.pack(fill='both', expand=True, padx=30, pady=10)
    tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
    for col in columns:
        tree.heading(col, text=col, command=lambda c=col: sort_column(tree, c, False))
        tree.column(col, anchor='center', width=180)
    for row in rows:
        tree.insert('', 'end', values=row)

    def on_right_click(event):
        try:
            item_id = tree.identify_row(event.y)
            if item_id:
                tree.selection_set(item_id)
                account_name = tree.item(item_id, "values")[0]
                
                context_menu = tk.Menu(app.root, tearoff=0)
                context_menu.add_command(label=f"Delete Account: {account_name}", command=lambda: confirm_delete(account_name))
                context_menu.tk_popup(event.x_root, event.y_root)
        except Exception as e:
            messagebox.showerror("Error", f"Could not process right-click event: {e}")

    def confirm_delete(account_name):
        if delete_account(account_name):
            # Refresh the view if deletion was successful
            show_accounts_view(app)

    tree.bind("<Button-3>", on_right_click) # Bind right-click

    vsb = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=vsb.set)
    tree.pack(side='left', fill='both', expand=True)
    vsb.pack(side='right', fill='y')
