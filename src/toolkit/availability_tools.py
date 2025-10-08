import pandas as pd
from typing import Literal
from langchain_core.tools import tool 
from models.data_models import *
from utils.helpers import convert_am_to_pm



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

    df = pd.read_csv("data/doctor_availability.csv")


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

@tool 
def check_availability_by_specialisation(
    desired_date: DateModel, 
    specialization: Literal[
            "general_dentist", 
            "cosmetic_dentist", 
            "prosthodontist", 
            "pediatric_dentist", 
            "emergency_dentist", 
            "oral_surgeon", 
            "orthodontist"
        ]
): 
    """
    Checking the database if we have availability for the specific specialistion. 

    The parameters should be mentioned by the user in the query.
    """

    df = pd.read_csv("data/doctor_availability.csv")
    df["time_slot"] = df["date_slot"].str.split(" ", expand=True).iloc[:, 1]

    
    rows = df[
            (df["date_slot"] == desired_date.date) &
            (df["specialization"] == specialization) &
            (df["is_available"] == True)

    ].groupby(["specialization", "doctor_name"])["date_slot_time"].apply(list).reset_index(name="available_slots")

    if len(rows) == 0: 
        output = "no availability for the the entire day"
    else: 
        output = f"this availability for {desired_date.date}\n"
        for row in rows.values: 
            output += row[1] + ". available slots: \n" + ", \n".join([convert_am_to_pm(value) for value in row[2]])
    return output