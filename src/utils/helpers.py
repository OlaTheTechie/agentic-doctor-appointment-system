from datetime import datetime

def convert_datetime_format(date_str):
    date = datetime.strptime(date_str, "%d-%m-%Y %H:%M")
    return date.strftime("%d-%m-%Y %-H.%M")  

def convert_am_to_pm(time_str):
    time_str = str(time_str)
    hours, minutes = map(int, time_str.split(":"))

    period = "AM" if hours < 12 else "PM"
    hours = hours % 12 or 12

    return f"{hours}:{minutes:02d} {period}"
