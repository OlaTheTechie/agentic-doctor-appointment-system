import pandas as pd
from typing import Literal
from langchain_core.tools import tool 
from src.models.data_models import *
from src.utils.helpers import convert_am_to_pm

DATA_PATH = "data/doctor_availability.csv"


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
    Checking the database to see if there is availability for the specific doctor on the given day.
    The parameters should be mentioned by the user in the given query.
    """
    df = pd.read_csv(DATA_PATH)
    df[["date_slot", "time_slot"]] = df["date_slot"].str.split(" ", expand=True)

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
        output = f"the availability for the date {desired_date.date}\n"
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
    Checking the database if we have availability for the specific specialization. 
    The parameters should be mentioned by the user in the query.
    """
    df = pd.read_csv(DATA_PATH)
    df[["date_slot", "time_slot"]] = df["date_slot"].str.split(" ", expand=True)

    rows = (
        df[
            (df["date_slot"] == desired_date.date) &
            (df["specialization"] == specialization) &
            (df["is_available"] == True)
        ]
        .groupby(["specialization", "doctor_name"])["time_slot"]
        .apply(list)
        .reset_index(name="available_slots")
    )

    if len(rows) == 0: 
        output = "no availability for the entire day"
    else: 
        output = f"availability for {desired_date.date}\n"
        for row in rows.values: 
            output += f"{row[1]}. available slots: " + ", ".join([convert_am_to_pm(value) for value in row[2]]) + "\n"

    return output
