import db_connect
from tkinter import messagebox
from utils import parse_date

def process_pending_transaction(pending_id, action, success_callback=None):
    conn = db_connect.get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Get the pending transaction details
        cursor.execute("SELECT * FROM pending_transactions WHERE id = %s", (pending_id,))
        transaction = cursor.fetchone()

        if not transaction:
            messagebox.showerror("Error", "Pending transaction not found.")
            return

        if action == 'approve':
            # Move to the final table (payments or receipts)
            if transaction['transaction_type'] == 'payment':
                # This logic is moved from the original add_payment.py
                from add_payment import add_payment_to_final_tables
                add_payment_to_final_tables(conn, cursor, transaction)
            elif transaction['transaction_type'] == 'receipt':
                from add_receipt import add_receipt_to_final_table
                add_receipt_to_final_table(conn, cursor, transaction)
            
            # Delete from pending_transactions after successful processing
            cursor.execute("DELETE FROM pending_transactions WHERE id = %s", (pending_id,))
            messagebox.showinfo("Success", "Transaction approved and recorded.")
            if success_callback:
                success_callback()

        elif action == 'reject':
            if messagebox.askyesno("Confirm Reject", "Are you sure you want to reject this transaction?"):
                cursor.execute("DELETE FROM pending_transactions WHERE id = %s", (pending_id,))
                messagebox.showinfo("Success", "Transaction rejected.")
                if success_callback:
                    success_callback()

        conn.commit()

    except Exception as e:
        conn.rollback()
        messagebox.showerror("Error", f"An error occurred: {e}")
    
    finally:
        cursor.close()
        conn.close()

def get_pending_transaction_count():
    """Gets the number of pending transactions."""
    conn = db_connect.get_connection()
    cursor = conn.cursor()
    # Any transaction in this table is considered pending.
    cursor.execute("SELECT COUNT(*) FROM pending_transactions")
    count = cursor.fetchone()[0]
    conn.close()
    return count
