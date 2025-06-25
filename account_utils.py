import db_connect
from tkinter import messagebox

def delete_account(account_name):
    conn = db_connect.get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Check for dependencies in other tables
        dependencies = {
            'payments': 'account_name',
            'receipts': 'account_name',
            'journal_entries': 'account_name',
            'fd_details': 'bank_account'
        }

        for table, column in dependencies.items():
            query = f"SELECT COUNT(*) as count FROM {table} WHERE {column} = %s"
            cursor.execute(query, (account_name,))
            result = cursor.fetchone()
            if result['count'] > 0:
                messagebox.showerror("Delete Failed", f"Cannot delete account '{account_name}' because it has associated records in the '{table}' table.")
                return False

        # If no dependencies, ask for confirmation and delete
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete the account '{account_name}'? This action cannot be undone."):
            cursor.execute("DELETE FROM accounts WHERE account_name = %s", (account_name,))
            conn.commit()
            messagebox.showinfo("Success", f"Account '{account_name}' has been deleted successfully.")
            return True
        else:
            return False

    except Exception as e:
        conn.rollback()
        messagebox.showerror("Error", f"An error occurred while trying to delete the account: {e}")
        return False

    finally:
        cursor.close()
        conn.close()
