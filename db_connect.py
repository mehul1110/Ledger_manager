import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="EMEJOURNAL",
        user="root",
        password="0000",
        database="ledger_db",
        port = 3307
    )
