#!/usr/bin/env python3
"""
comprehensive tool testing for multi-agent system
tests all data models, helper functions, and tools
"""

import pandas as pd
from datetime import date, datetime
from src.models.data_models import DateModel, DateTimeModel, IDNumberModel
from src.utils.helpers import convert_datetime_format, convert_am_to_pm
from src.toolkit.availability_tools import check_availability_by_doctor, check_availability_by_specialisation
from src.toolkit.appointment_tools import set_appointment, cancel_appointment

def test_data_models():
    """test pydantic data models"""
    print("\ntesting data models")
    print("-" * 40)
    
    # test datemodel
    try:
        valid_date = DateModel(date="16-10-2025")
        print(f"datemodel valid: {valid_date.date}")
    except Exception as e:
        print(f"datemodel failed: {e}")
    
    try:
        invalid_date = DateModel(date="2025-10-16")  # wrong format
        print(f"datemodel should have failed but didn't: {invalid_date.date}")
    except Exception as e:
        print(f"datemodel correctly rejected invalid format: {e}")
    
    # test datetimemodel
    try:
        valid_datetime = DateTimeModel(date="16-10-2025 14:30")
        print(f"datetimemodel valid: {valid_datetime.date}")
    except Exception as e:
        print(f"datetimemodel failed: {e}")
    
    # test idnumbermodel
    try:
        valid_id = IDNumberModel(id=12345678)
        print(f"idnumbermodel valid: {valid_id.id}")
    except Exception as e:
        print(f"idnumbermodel failed: {e}")

def test_helper_functions():
    """test helper functions"""
    print("\ntesting helper functions")
    print("-" * 40)
    
    # test convert_datetime_format
    try:
        result = convert_datetime_format("16-10-2025 14:30")
        print(f"convert_datetime_format: '16-10-2025 14:30' -> '{result}'")
    except Exception as e:
        print(f"convert_datetime_format failed: {e}")
    
    # test convert_am_to_pm
    try:
        result1 = convert_am_to_pm("09:30")
        result2 = convert_am_to_pm("14:30")
        print(f"convert_am_to_pm: '09:30' -> '{result1}', '14:30' -> '{result2}'")
    except Exception as e:
        print(f"convert_am_to_pm failed: {e}")

def test_data_file():
    """test the data file structure"""
    print("\ntesting data file")
    print("-" * 40)
    
    try:
        df = pd.read_csv("data/doctor_availability.csv")
        print(f"data file loaded: {len(df)} rows")
        print(f"columns: {list(df.columns)}")
        
        # check data structure
        print(f"date range: {df['date_slot'].min()} to {df['date_slot'].max()}")
        print(f"doctors: {df['doctor_name'].nunique()} unique doctors")
        print(f"specializations: {df['specialization'].nunique()} unique specializations")
        
        # show sample data
        print("\nsample data:")
        print(df.head(3).to_string())
        
        # check today's data
        today_str = date.today().strftime("%d-%m-%Y")
        today_data = df[df['date_slot'].str.startswith(today_str)]
        print(f"\ntoday's data ({today_str}): {len(today_data)} slots")
        
        return True
        
    except Exception as e:
        print(f"data file error: {e}")
        return False

def test_availability_tools():
    """test availability checking tools"""
    print("\ntesting availability tools")
    print("-" * 40)
    
    # test check_availability_by_doctor
    try:
        date_model = DateModel(date="16-10-2025")
        result = check_availability_by_doctor(date_model, "jane smith")
        print(f"check_availability_by_doctor result:")
        print(f"   {result}")
    except Exception as e:
        print(f"check_availability_by_doctor failed: {e}")
    
    # test check_availability_by_specialisation
    try:
        date_model = DateModel(date="16-10-2025")
        result = check_availability_by_specialisation(date_model, "general_dentist")
        print(f"check_availability_by_specialisation result:")
        print(f"   {result[:200]}...")
    except Exception as e:
        print(f"check_availability_by_specialisation failed: {e}")

def test_appointment_tools():
    """test appointment management tools"""
    print("\ntesting appointment tools")
    print("-" * 40)
    
    # test set_appointment
    try:
        datetime_model = DateTimeModel(date="16-10-2025 14:30")
        id_model = IDNumberModel(id=12345678)
        result = set_appointment(datetime_model, id_model, "jane smith")
        print(f"set_appointment result: {result}")
    except Exception as e:
        print(f"set_appointment failed: {e}")
    
    # test cancel_appointment (if we just booked one)
    try:
        datetime_model = DateTimeModel(date="16-10-2025 14:30")
        id_model = IDNumberModel(id=12345678)
        result = cancel_appointment(datetime_model, id_model, "jane smith")
        print(f"cancel_appointment result: {result}")
    except Exception as e:
        print(f"cancel_appointment failed: {e}")

def identify_tool_issues():
    """identify specific issues with the tools"""
    print("\nidentifying tool issues")
    print("-" * 40)
    
    # check data file format
    try:
        df = pd.read_csv("data/doctor_availability.csv")
        sample_date = df['date_slot'].iloc[0]
        print(f"data file date format: '{sample_date}'")
        
        # check if it matches expected format
        if "-" in sample_date and len(sample_date.split("-")) == 3:
            print("data file uses dd-mm-yyyy format")
        else:
            print("warning: unexpected date format in data file")
    except Exception as e:
        print(f"error reading data file: {e}")
    
    # test helper function conversion
    try:
        test_date = "16-10-2025 14:30"
        converted = convert_datetime_format(test_date)
        print(f"helper conversion: '{test_date}' -> '{converted}'")
        
        # check if converted format matches csv format
        if converted and "-" in converted:
            print("helper function produces compatible format")
        else:
            print("warning: helper function may not produce compatible format")
    except Exception as e:
        print(f"helper function error: {e}")

def main():
    """run comprehensive tool testing"""
    print("comprehensive tool testing for multi-agent system")
    print("=" * 60)
    
    # run all tests
    test_data_models()
    test_helper_functions()
    
    data_file_ok = test_data_file()
    if data_file_ok:
        test_availability_tools()
        test_appointment_tools()
    else:
        print("\nskipping tool tests due to data file issues")
    
    identify_tool_issues()
    
    print("\n" + "=" * 60)
    print("tool analysis summary")
    print("=" * 60)
    print("1. check data file format compatibility")
    print("2. verify helper function outputs")
    print("3. test tool functions with sample data")
    print("4. ensure error handling works correctly")

if __name__ == "__main__":
    main()