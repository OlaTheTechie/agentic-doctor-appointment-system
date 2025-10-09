import pandas as pd
from langchain_core.tools import tool
from typing import Literal
from src.models.data_models import *
from src.utils.helpers import convert_datetime_format

DATA_PATH = "data/doctor_availability.csv"


@tool
def set_appointment(
    desired_date: DateTimeModel,
    id_number: IDNumberModel,
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
    Set an appointment with the doctor.
    The parameters must be included in the query by the user.
    """
    df = pd.read_csv(DATA_PATH)

    availability_logic = (
        (df["date_slot"] == convert_datetime_format(desired_date.date))
        & (df["doctor_name"].str.lower() == doctor_name.lower())
        & (df["is_available"] == True)
    )

    available_cases = df[availability_logic]

    if len(available_cases) == 0:
        return "no available appointments for that particular case"
    else:
        df.loc[availability_logic, ["is_available", "patient_to_attend"]] = [False, id_number.id]
        df.to_csv(DATA_PATH, index=False)
        return "appointment has been successfully booked"


@tool
def cancel_appointment(
    date: DateTimeModel,
    id_number: IDNumberModel,
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
    Cancel an appointment.
    The parameters must be included in the query by the user.
    """
    df = pd.read_csv(DATA_PATH)

    occupied_state_logic = (
        (df["date_slot"] == date.date)
        & (df["patient_to_attend"] == id_number.id)
        & (df["doctor_name"].str.lower() == doctor_name.lower())
    )

    verified_occupied_states = df[occupied_state_logic]

    if len(verified_occupied_states) == 0:
        return "you don't have any appointment with that specification"
    else:
        df.loc[occupied_state_logic, ["is_available", "patient_to_attend"]] = [True, None]
        df.to_csv(DATA_PATH, index=False)
        return "appointment has been cancelled successfully"


@tool
def reschedule_appointment(
    old_date: DateTimeModel,
    new_date: DateTimeModel,
    id_number: IDNumberModel,
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
    Reschedule an appointment.
    The parameters must be included in the query by the user.
    """
    df = pd.read_csv(DATA_PATH)

    available_for_desired_date_logic = (
        (df["date_slot"] == new_date.date)
        & (df["is_available"] == True)
        & (df["doctor_name"].str.lower() == doctor_name.lower())
    )

    availability_for_desired_date = df[available_for_desired_date_logic]

    if len(availability_for_desired_date) == 0:
        return "no available slots for the desired period"
    else:
        # Terminate the former appointment
        cancel_appointment.invoke({
            "date": old_date,
            "id_number": id_number,
            "doctor_name": doctor_name
        })

        # Make another appointment for the new date
        set_appointment.invoke({
            "desired_date": new_date,
            "id_number": id_number,
            "doctor_name": doctor_name
        })

        return "appointment has been successfully rescheduled"
