import streamlit as st 
import requests 

API_URL = "http://127.0.0.1:8000/execute"

st.title("Doctors Appointement Multi-Agent System")

user_id = st.text_input("Enter your ID number here: ", "")

query = st.text_area("Enter your query: ", "Can you check if a dentist is avaliable tomorow at 10 AM?")

if st.button("Submit Query"): 
    if user_id and query: 
        try: 
            response = requests.post(API_URL, json={
                "messages": [
                    {"role": "user", "content": query}
                ], 
                "id_number": int(user_id)
            }, verify=False)

            if response.status_code == 200: 
                st.success("Response successfully received: ")
                print("============The response: ============")
                print(response.json())
                data = response.json()
                st.write(
                    data["messages"][-1]["content"]
                )
                
            else: 
                st.error(f"Error {response.status_code}: ")
                st.error("Could not process the request.")
        except Exception as e: 
            st.error(f"Exception occured: {e}")
    else: 
        st.warning("Please enter both ID and query")