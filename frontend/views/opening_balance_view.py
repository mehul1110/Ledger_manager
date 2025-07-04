import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import sys
import os

# Ensure the root directory is in the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from db_connect import get_connection
from journal_utils import insert_journal_entry

def show_opening_balance_view(app, go_back_callback):
    for widget in app.root.winfo_children():
        widget.destroy()
    app.set_background()

    frame = tk.Frame(app.root, bg='white', bd=2, relief='groove')
    frame.place(relx=0.5, rely=0.5, anchor='center')

    # --- Title and Back Button ---
    header_frame = tk.Frame(frame, bg='white')
    header_frame.pack(fill='x', padx=10, pady=10)
    
    tk.Button(header_frame, text="← Go Back", command=go_back_callback, font=("Arial", 12)).pack(side='left')
    ttk.Label(header_frame, text="Set Opening Balances", font=("Georgia", 16, "bold"), background='white').pack(side='left', padx=20)

    # --- Form ---
    form_frame = tk.Frame(frame, bg='white', padx=20, pady=20)
    form_frame.pack(fill='both', expand=True)

    fields = {
        "Bank Balance": "The main cash or bank account balance.",
        "FD Balance": "Total value of all Fixed Deposits.",
        "Fund Balance": "Balance of general-purpose funds.",
        "Property Balance": "Total value of all properties.",
        "Sundry Balance": "Net balance of all sundry credit/debit accounts.",
        "Cash Balance": "Balance of physical cash in hand.",
        "Effective Date": "The date these balances are effective from (e.g., start of financial year)."
    }
    
    entries = {}
    for i, (label, tooltip) in enumerate(fields.items()):
        ttk.Label(form_frame, text=label, font=("Arial", 12), background='white').grid(row=i, column=0, sticky='w', padx=10, pady=5)
        entry = ttk.Entry(form_frame, font=("Arial", 12), width=25)
        entry.grid(row=i, column=1, padx=10, pady=5)
        if label == "Effective Date":
            entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
        else:
            entry.insert(0, "0.00")
        entries[label.replace(" ", "_").lower()] = entry
        ttk.Label(form_frame, text=tooltip, font=("Arial", 9, "italic"), background='white', foreground='grey').grid(row=i, column=2, sticky='w', padx=10)

    def save_opening_balances():
        try:
            # --- Data Extraction ---
            balances = {
                'amount': float(entries['bank_balance'].get()),
                'fd': float(entries['fd_balance'].get()),
                'fund': float(entries['fund_balance'].get()),
                'property_value': float(entries['property_balance'].get()),
                'sundry': float(entries['sundry_balance'].get()),
                'cash': float(entries['cash_balance'].get())
            }
            effective_date_str = entries['effective_date'].get()
            effective_date = datetime.strptime(effective_date_str, '%Y-%m-%d').date()

            # --- Filter out zero balances ---
            balances_to_set = {k: v for k, v in balances.items() if v != 0.0}
            if not balances_to_set:
                messagebox.showinfo("No Balances", "No opening balances to set. All values are zero.")
                return

            # --- Confirmation ---
            confirm = messagebox.askyesno(
                "Confirm Opening Balances",
                "This will create permanent opening balance entries. This action should only be performed once.\n\nAre you sure you want to proceed?"
            )
            if not confirm:
                return

            # --- Database Interaction ---
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            # Check if an opening balance entry already exists
            cursor.execute("SELECT COUNT(*) as count FROM journal_entries WHERE narration LIKE 'Opening Balance: %%'")
            if cursor.fetchone()['count'] > 0:
                messagebox.showwarning("Already Exists", "Opening balance entries already exist. You cannot create more. To make changes, please adjust the existing journal entries manually.")
                cursor.close()
                conn.close()
                return

            # Get the last id to generate a new one for entry_id
            cursor.execute("SELECT MAX(id) as max_id FROM journal_entries")
            result = cursor.fetchone()
            last_id = result['max_id'] if result and result['max_id'] is not None else 0
            
            # Create a separate journal entry for each non-zero balance
            i = 1
            for balance_type, value in balances_to_set.items():
                narration = f"Opening Balance: {balance_type.replace('_', ' ').title()}"
                new_entry_id = f"OB{last_id + i:05d}"
                i += 1

                # Prepare arguments for insert_journal_entry
                j_amount = value if balance_type == 'amount' else None
                j_fd = value if balance_type == 'fd' else None
                j_fund = value if balance_type == 'fund' else None
                j_property = value if balance_type == 'property_value' else None
                j_sundry = value if balance_type == 'sundry' else None
                j_cash = value if balance_type == 'cash' else None

                insert_journal_entry(
                    db_connection=conn,
                    entry_id=new_entry_id,
                    account_name="Opening Balance",
                    entry_type='System',
                    amount=j_amount,
                    narration=narration,
                    mop=None,
                    entry_date=effective_date,
                    fd=j_fd,
                    sundry=j_sundry,
                    property_value=j_property,
                    fund=j_fund,
                    cash=j_cash
                )

            conn.commit()
            messagebox.showinfo("Success", "Opening balances have been set successfully.")
            go_back_callback()

        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numbers for balances and a valid date (YYYY-MM-DD).")
        except Exception as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()

    save_button = ttk.Button(form_frame, text="Save Opening Balances", command=save_opening_balances)
    save_button.grid(row=len(fields), columnspan=3, pady=20)
