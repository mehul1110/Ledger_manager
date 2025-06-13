from db_connect import get_connection
from journal_utils import insert_journal_entry
from datetime import date

def approve_fd_maturity():
    conn = get_connection()
    cursor = conn.cursor()
    today = date.today()

    # Find all matured but unapproved FDs
    cursor.execute("""
        SELECT payment_id, bank_account, amount, interest_rate, maturity_amount, maturity_date
        FROM fd_details
        WHERE maturity_date <= %s AND status = 'Matured'
    """, (today,))
    matured_fds = cursor.fetchall()

    if not matured_fds:
        print("No matured pending FD to approve.")
        cursor.close()
        conn.close()
        return

    for fd in matured_fds:
        payment_id, bank_account, amount, interest_rate, maturity_amount, maturity_date = fd
        print(f"\nFD {payment_id} matured on {maturity_date} in {bank_account}:")
        print(f"  Principal: {amount}")
        print(f"  Interest Rate: {interest_rate}%")
        print(f"  Maturity Amount: {maturity_amount}")
        approve = input("Approve this FD maturity? (y/n): ").strip().lower()
        if approve == 'y':
            interest_gained = float(maturity_amount) - float(amount)
            # Insert payment for total maturity amount
            narration = f"FD matured: Principal + Interest"
            cursor.execute("""
                INSERT INTO payments (account_name, amount, mop, cheque_no, narration, date)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (bank_account, maturity_amount, 'Bank Transfer', None, narration, maturity_date))
            conn.commit()
            cursor.execute("SELECT payment_id FROM payments ORDER BY id DESC LIMIT 1")
            payment_id_new = cursor.fetchone()[0]
            # Only add the interest to main fund as a Debit, and in fd column
            if interest_gained > 0:
                narration_interest = f"FD matured: Interest received"
                insert_journal_entry(conn, 'main fund', 'Debit', 0, narration_interest, 'Bank Transfer', None, maturity_date, fd=interest_gained)
            # Mark as approved and remove from fd_details
            cursor.execute("""
                DELETE FROM fd_details WHERE payment_id = %s
            """, (payment_id,))
            print(f"✅ FD {payment_id} maturity approved, posted, and removed from fd_details.")
        else:
            print(f"⏸️ FD {payment_id} left pending.")
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    approve_fd_maturity()
