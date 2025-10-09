from pydantic import BaseModel, Field, field_validator
import re


class DateTimeModel(BaseModel):
    date: str = Field(
        description="properly formatted date",
        pattern=r'^\d{2}-\d{2}-\d{4} \d{2}:\d{2}$'
    )

    @field_validator("date")
    def check_date_format(cls, v):
        if not re.match(r'^\d{2}-\d{2}-\d{4} \d{2}:\d{2}$', v):
            raise ValueError("The date should be in format 'DD-MM-YYYY HH:MM'")
        return v


class DateModel(BaseModel):
    date: str = Field(
        description="properly formatted date",
        pattern=r'^\d{2}-\d{2}-\d{4}$'
    )

    @field_validator("date")
    def check_date_format(cls, v):
        if not re.match(r'^\d{2}-\d{2}-\d{4}$', v):
            raise ValueError("The date must be in this format 'DD-MM-YYYY'")
        return v


class IDNumberModel(BaseModel):
    id: int = Field(
        description="identification number (7 or 8 digits long)",
    )

    @field_validator("id")
    def check_id_format(cls, v):
        if not re.match(r'^\d{7,8}$', str(v)):
            raise ValueError("The ID number should be a 7 or 8 digit number")
        return v
