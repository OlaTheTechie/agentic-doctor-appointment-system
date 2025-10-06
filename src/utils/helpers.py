from datetime import datetime 

def convert_datetime_format(date_str): 

    date = datetime.strptime(date_str, "%d-%m-%Y %H:%M")
    return date.strftime("%d-%m-%Y %#H.%M")