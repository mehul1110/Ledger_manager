from db_connect import get_connection
from datetime import datetime, timedelta

def depreciate_property_assets():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Only depreciate non-expendable items older than 2 years
        two_years_ago = datetime.today() - timedelta(days=2*365)
        cursor.execute("""
            UPDATE property_details
            SET value = ROUND(value * (1 - depreciation_rate/100), 2)
            WHERE description = 'non-expendable'
              AND purchase_date <= %s
        """, (two_years_ago.date(),))
        conn.commit()
        print(f"✅ Depreciation applied to all non-expendable property items older than 2 years for FY {get_financial_year()}.")
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
