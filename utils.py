from datetime import datetime, date

def parse_date(input_str):
    try:
        return datetime.strptime(input_str, "%d-%m-%Y").date()
    except ValueError:
        print("❌ Invalid date format. Please use DD-MM-YYYY.")
        return None

def get_today_str():
    return datetime.now().strftime('%d-%m-%Y')
