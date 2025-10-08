from datetime import datetime 

def convert_datetime_format(date_str): 

    date = datetime.strptime(date_str, "%d-%m-%Y %H:%M")
    return date.strftime("%d-%m-%Y %#H.%M")

def convert_am_to_pm(time_str): 
    # split the time string into hours and minutes 
    time_str = str(time_str)
    hours, minutes = map(int, time_str.split(":"))

    # determine AM or PM
    period = "AM" if hours < 12 else "PM"

    # convert hours to 12-hour format
    hours = hours % 12 or 12

    # formate the output 
    return f"{hours}: {minutes:.02d} {period}"