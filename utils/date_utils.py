from datetime import datetime, timedelta

def generate_days(start_day, ndays):
    days = []
    current_day = datetime.strptime(start_day, '%Y-%m-%d')
    for _ in range(ndays):
        days.append(current_day.strftime('%Y-%m-%d'))
        current_day += timedelta(days=1)
    return days
  
def is_weekend(day_str):
    date_obj = datetime.strptime(day_str, '%Y-%m-%d')
    return date_obj.weekday() >= 5  # 5 is Saturday, 6 is Sunday
