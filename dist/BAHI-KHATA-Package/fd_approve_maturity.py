from db_connect import get_connection
from datetime import date

def approve_fd_maturity():
    """
    This function now adds FD maturity transactions to the pending_transactions table
    for approval through the standard workflow, instead of directly posting to final tables.
    """
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
        approve = input("Submit FD maturity for approval? (y/n): ").strip().lower()
        
        if approve == 'y':
            # Submit the FD maturity transaction to pending_transactions for approval
            narration = f"FD maturity payment from {bank_account}"
            
            cursor.execute("""
                INSERT INTO pending_transactions (
                    transaction_type, account_name, amount, mop, narration, transaction_date, remarks,
                    author, item_name, description, property_type, fd_duration, fd_interest
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                'payment',  # transaction_type
                bank_account,  # account_name
                float(maturity_amount),  # amount (full maturity amount)
                'Bank Transfer',  # mop
                narration,  # narration
                maturity_date,  # transaction_date
                f"FD maturity: Original payment ID {payment_id}",  # remarks
                None,  # author
                f"FD Maturity {payment_id}",  # item_name
                f"Principal: {amount}, Interest: {float(maturity_amount) - float(amount)}",  # description
                'fd_maturity',  # property_type (special marker for FD maturity)
                None,  # fd_duration
                None   # fd_interest
            ))
            
            # Update FD status to indicate it's submitted for approval
            cursor.execute("""
                UPDATE fd_details 
                SET status = 'Maturity Submitted' 
                WHERE payment_id = %s
            """, (payment_id,))
            
            print(f"✅ FD {payment_id} maturity submitted for approval workflow.")
        else:
            print(f"⏸️ FD {payment_id} left pending.")
    
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    approve_fd_maturity()
