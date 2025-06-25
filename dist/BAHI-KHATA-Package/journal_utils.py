import mysql.connector

def insert_journal_entry(db_connection, entry_id, account_name, entry_type, amount, narration, mop, entry_date, fd=None, sundry=None, property=None):
    """
    Inserts a journal entry into the journal_entries table.
    The amount for FD, Sundry, or Property transactions is entered in the respective column, not in the 'amount' column.
    Only one of fd, sundry, property should be set per entry; all others must be None.
    Enforces that entry_type is either 'Bank' or 'Fund'.
    """
    print(f"[DEBUG] insert_journal_entry: entry_id={repr(entry_id)}, entry_type={repr(entry_type)}, account_name={repr(account_name)}, amount={repr(amount)}, narration={repr(narration)}, mop={repr(mop)}, entry_date={repr(entry_date)}, fd={repr(fd)}, sundry={repr(sundry)}, property={repr(property)}")
    if entry_type not in ("Bank", "Fund"):
        raise ValueError(f"Invalid entry_type '{entry_type}'. Must be 'Bank' or 'Fund'.")
    try:
        cursor = db_connection.cursor()
        query = """
            INSERT INTO journal_entries
            (entry_id, account_name, entry_type, amount, narration, mop, entry_date, fd, sundry, property)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        # Only one of fd, sundry, property should have the transaction amount, others None
        if fd is not None:
            values = (entry_id, account_name, entry_type, None, narration, mop, entry_date, fd, None, None)
        elif sundry is not None:
            values = (entry_id, account_name, entry_type, None, narration, mop, entry_date, None, sundry, None)
        elif property is not None:
            values = (entry_id, account_name, entry_type, None, narration, mop, entry_date, None, None, property)
        else:
            values = (entry_id, account_name, entry_type, amount, narration, mop, entry_date, None, None, None)
        print(f"[DEBUG] SQL values: {values}")
        cursor.execute(query, values)
        db_connection.commit()
    except mysql.connector.Error as err:
        print(f"❌ Error inserting journal entry: {err}")
        db_connection.rollback()
    finally:
        cursor.close()
