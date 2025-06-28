from db_connect import get_connection

def add_account(name=None, acc_type=None):
    conn = get_connection()
    cursor = conn.cursor()
    if name is None or acc_type is None:
        raise ValueError("Both 'name' and 'acc_type' must be provided.")
    try:
        cursor.execute("INSERT INTO accounts (account_name, account_type) VALUES (%s, %s)", (name, acc_type))
        conn.commit()
        print("✅ Account added.")
    except Exception as e:
        print("❌ Error:", e)
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    add_account()
