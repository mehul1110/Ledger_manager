import mysql.connector

def insert_journal_entry(db_connection, account_name, entry_type, amount, narration, mop, cheque_no, entry_date, fd=None, sundry=None, property=None):
    """
    Inserts a journal entry into the journal_entries table.
    The amount for FD, Sundry, or Property transactions is entered in the respective column, not in the 'amount' column.
    Only one of fd, sundry, property should be set per entry; all others must be None.
    """
    try:
        cursor = db_connection.cursor()
        query = """
            INSERT INTO journal_entries
            (account_name, entry_type, amount, narration, mop, cheque_no, entry_date, fd, sundry, property)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        # Only one of fd, sundry, property should have the transaction amount, others None
        if fd is not None:
            values = (account_name, entry_type, None, narration, mop, cheque_no, entry_date, fd, None, None)
        elif sundry is not None:
            values = (account_name, entry_type, None, narration, mop, cheque_no, entry_date, None, sundry, None)
        elif property is not None:
            values = (account_name, entry_type, None, narration, mop, cheque_no, entry_date, None, None, property)
        else:
            values = (account_name, entry_type, amount, narration, mop, cheque_no, entry_date, None, None, None)
        cursor.execute(query, values)
        db_connection.commit()
    except mysql.connector.Error as err:
        print(f"❌ Error inserting journal entry: {err}")
        db_connection.rollback()
    finally:
        cursor.close()
