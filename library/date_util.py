from datetime import datetime, date, timedelta
def today_plus(plus):
    date_plus(datetime.now(), plus)

def date_plus(date, plus):
    date + timedelta(days=plus)

def is_after(date1, date2):
    if not isinstance(date1, date):
        date1 = format_date(date1, "%Y-%m-%d")
    if not isinstance(date2, date):
        date2 = format_date(date2, "%Y-%m-%d")
    return date1 > date2

def is_before(date1, date2):
    if not isinstance(date1, date):
        date1 = format_date(date1, "%Y-%m-%d")
    if not isinstance(date2, date):
        date2 = format_date(date2, "%Y-%m-%d")
    return date1 > date2

def format_date(date_str, format):
    return datetime.strptime(date_str, format)

def today():
    return datetime.today