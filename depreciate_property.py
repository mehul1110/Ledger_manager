from db_connect import get_connection
from datetime import datetime

def depreciate_property_assets():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Only depreciate non-expendable items
        cursor.execute("""
            UPDATE property_details
            SET new_rate = ROUND(new_rate * (1 - depreciation_rate/100), 2)
            WHERE description = 'non-expendable'
        """)
        conn.commit()
        print(f"✅ Depreciation applied to all non-expendable property items for FY {get_financial_year()}.")
    except Exception as e:
        print(f"❌ Error during depreciation: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def get_financial_year():
    today = datetime.today()
    year = today.year
    if today.month < 4:
        return f"{year-1}-{year}"
    else:
        return f"{year}-{year+1}"

if __name__ == "__main__":
    depreciate_property_assets()
