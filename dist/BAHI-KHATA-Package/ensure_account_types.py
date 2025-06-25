import mysql.connector

def ensure_account_types():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="123456",
        database="ledger_db"
    )
    cursor = conn.cursor()
    types = ['main fund', 'bank', 'cash', 'salary', 'unit', 'printer', 'payer', 'payee']
    for t in types:
        try:
            cursor.execute("INSERT IGNORE INTO account_types (account_type) VALUES (%s)", (t,))
        except Exception as e:
            print(f"Error inserting {t}: {e}")
    conn.commit()
    cursor.close()
    conn.close()
    print("Account types ensured.")

if __name__ == "__main__":
    ensure_account_types()
