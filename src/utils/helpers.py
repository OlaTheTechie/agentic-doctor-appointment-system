from datetime import datetime

def convert_datetime_format(date_str):
    """Convert datetime string to match CSV format"""
    try:
        # parse the input format dd-mm-yyyy hh:mm
        date = datetime.strptime(date_str, "%d-%m-%Y %H:%M")
        # return in csv format dd-mm-yyyy hh:mm (with colon, not dot)
        return date.strftime("%d-%m-%Y %H:%M")
    except ValueError as e:
        print(f"Date conversion error: {e}")
        return date_str  # Return original if conversion fails  

def convert_am_to_pm(time_str):
    time_str = str(time_str)
    hours, minutes = map(int, time_str.split(":"))

    period = "AM" if hours < 12 else "PM"
    hours = hours % 12 or 12

    return f"{hours}:{minutes:02d} {period}"
