from db_connect import get_connection

def add_account():
    conn = get_connection()
    cursor = conn.cursor()

    name = input("Enter new account name (unique): ").strip()
    acc_type = input("Enter account type (main fund, bank, cash , salary, unit , printer): ").strip().lower()


    try:
        cursor.execute("INSERT INTO accounts (account_name, account_type) VALUES (%s, %s)", (name, acc_type))
        conn.commit()
        print("✅ Account added.")
    except Exception as e:
        print("❌ Error:", e)
    finally:
        cursor.close()
        conn.close()

# Run this to test:
# add_account()
