import pandas as pd
from typing import Literal
from langchain_core.tools import tool 
from models.data_models import *

df = pd.read_csv("data/doctor_availability.csv")


@tool
def check_availability_by_doctor(
    desired_date: DateModel, 
    doctor_name: Literal[
        "kevin anderson", 
        "robert martinez", 
        "susan davis", 
        "daniel miller", 
        "sarah wilson",
        "michael green", 
        "lisa brown", 
        "jane smith", 
        "emily johnson", 
        "john doe"
    ]
): 

    """
    Checking the database to see if there is availability for the specific doctor in the given day

    The parameters should be mentioned by the user in the given query
    """

    df["date_slot", "time_slot"] = df["date_slot"].str.split(" ", expand=True)

    available_rows = list(
        df[
            (df["date_slot"] == desired_date.date) &
            (df["doctor_name"] == doctor_name) &
            (df["is_available"] == True)

        ]["time_slot"]
    )

    if len(available_rows) == 0: 
        output = "no availability in the entire day"
    else: 
        output = f"the evailability for the date {desired_date.date}\n"
        output += "available slots: " + ", ".join(available_rows)

    return output
