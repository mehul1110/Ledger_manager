from datetime import datetime

def parse_date(input_str):
    try:
        return datetime.strptime(input_str, "%d-%m-%Y").date()
    except ValueError:
        print("❌ Invalid date format. Please use DD-MM-YYYY.")
        return None
