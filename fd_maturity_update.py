from db_connect import get_connection
from datetime import date

def process_fd_maturities():
    conn = get_connection()
    cursor = conn.cursor()
    today = date.today()

    # Find all matured FDs
    cursor.execute("""
        SELECT payment_id, bank_account, amount, interest_rate, maturity_amount, maturity_date
        FROM fd_details
        WHERE maturity_date <= %s AND status = 'Active'
    """, (today,))
    matured_fds = cursor.fetchall()

    for fd in matured_fds:
        payment_id, bank_account, amount, interest_rate, maturity_amount, maturity_date = fd

        # Mark FD as matured
        cursor.execute("""
            UPDATE fd_details SET status = 'Matured' WHERE payment_id = %s
        """, (payment_id,))
        print(f"✅ FD {payment_id} marked as matured.")

    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    process_fd_maturities()
