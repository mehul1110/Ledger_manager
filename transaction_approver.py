import db_connect
from tkinter import messagebox
from utils import parse_date
from notification_utils import create_notification

def ensure_account_exists(cursor, account_name, is_custom_account=False):
    """
    Ensure an account exists in the accounts table.
    If it doesn't exist, create it with appropriate account type.
    """
    try:
        # Check if account exists - use a simple query that works with dictionary cursor
        cursor.execute("SELECT COUNT(*) as count FROM accounts WHERE account_name = %s", (account_name,))
        result = cursor.fetchone()
        
        # Since we're using dictionary=True cursor, result is a dict
        if result is None:
            count = 0
        else:
            count = result.get('count', 0) or 0
            
        exists = count > 0
        
        if not exists:
            # Set account type based on whether it's a custom input
            account_type = 'custom' if is_custom_account else 'cash'
            
            # Create the account with appropriate type
            cursor.execute(
                "INSERT INTO accounts (account_name, account_type) VALUES (%s, %s)",
                (account_name, account_type)
            )
            print(f"✅ Created new account: {account_name} (type: {account_type})")
            return True
        
        print(f"ℹ️ Account '{account_name}' already exists")
        return False
        
    except Exception as e:
        error_msg = str(e) if str(e) else f"Unknown database error (type: {type(e).__name__})"
        print(f"❌ Error ensuring account exists: {error_msg}")
        raise Exception(f"Failed to ensure account '{account_name}' exists: {error_msg}")

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
            # Ensure the account exists before processing
            account_name = transaction['account_name']
            account_created = ensure_account_exists(cursor, account_name)
            
            if account_created:
                messagebox.showinfo(
                    "Account Created", 
                    f"✅ New account '{account_name}' was automatically created during approval."
                )
            
            # Move to the final table (payments or receipts)
            if transaction['transaction_type'] == 'payment':
                # This logic is moved from the original add_payment.py
                from add_payment import add_payment_to_final_tables
                add_payment_to_final_tables(conn, cursor, transaction)
            elif transaction['transaction_type'] == 'receipt':
                from add_receipt import add_receipt_to_final_table
                add_receipt_to_final_table(conn, cursor, transaction)
            
            # Create notification for approved transaction
            entry_id = transaction.get('entry_id') or transaction.get('id') or pending_id
            create_notification(str(entry_id), 'approved')
            
            # Delete from pending_transactions after successful processing
            cursor.execute("DELETE FROM pending_transactions WHERE id = %s", (pending_id,))
            messagebox.showinfo("Success", "✅ Transaction approved and recorded successfully!")
            if success_callback:
                success_callback()

        elif action == 'reject':
            if messagebox.askyesno("Confirm Reject", "Are you sure you want to reject this transaction?"):
                # Create notification for rejected transaction
                entry_id = transaction.get('id') or pending_id
                create_notification(str(entry_id), 'rejected')
                
                cursor.execute("DELETE FROM pending_transactions WHERE id = %s", (pending_id,))
                messagebox.showinfo("Success", "Transaction rejected.")
                if success_callback:
                    success_callback()

        conn.commit()

    except Exception as e:
        conn.rollback()
        error_msg = str(e) if str(e) else f"Unknown error occurred (type: {type(e).__name__})"
        
        # Handle the case where the error message is just "0" or empty
        if error_msg == "0" or error_msg.strip() == "":
            error_msg = "An unexpected error occurred during transaction processing. Please check the transaction details and try again."
        
        # Handle specific foreign key constraint errors
        if "foreign key constraint fails" in error_msg.lower():
            if "account_name" in error_msg:
                messagebox.showerror(
                    "Account Error", 
                    f"❌ Error: The account '{transaction.get('account_name', 'Unknown')}' could not be created or validated.\n\n"
                    f"Please check the account name and try again."
                )
            else:
                messagebox.showerror("Database Error", f"❌ Database constraint error: {error_msg}")
        else:
            messagebox.showerror("Error", f"❌ An error occurred during approval: {error_msg}")
        
        # Log the error with more details
        from datetime import datetime
        with open("error.log", "a") as log_file:
            log_file.write(f"{datetime.now()} - Error in process_pending_transaction: {error_msg} (Exception type: {type(e).__name__}, Transaction ID: {pending_id})\n")
    
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
