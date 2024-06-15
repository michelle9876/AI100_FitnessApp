import streamlit as st
from openai import OpenAI
import pandas as pd
from datetime import datetime, timedelta
import os
# Load and preprocess the dataset
df = pd.read_csv('exercises.csv')
df.fillna('', inplace=True)
df['Rating'] = df['Rating'].apply(lambda x: float(x) if x != '' else 0.0)

# Using Secrets API to get API key from environment variables
os.environ["OPENAI_API_KEY"] = st.secrets['API_KEY']
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))



def generate_workout_plan(user_preferences, duration, start_date):
    try:
        messages = [
            {"role": "system", "content": "You are a fitness coach."},
            {"role": "user", "content": f"Create a {duration} workout plan starting from {start_date.strftime('%Y-%m-%d')} for a user with the following preferences: {user_preferences}. The plan should include different exercises from the dataset provided and be well-balanced."}
        ]

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
        )

        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None

# Function to calculate dates based on selected duration
def calculate_dates(duration, start_date):
    dates = []
    if duration == "1 Week":
        for i in range(7):  # 7 days for 1 week
            day = start_date + timedelta(days=i)
            dates.append(day.strftime('%Y-%m-%d'))
    elif duration == "2 Weeks":
        for i in range(14):  # 14 days for 2 weeks
            day = start_date + timedelta(days=i)
            dates.append(day.strftime('%Y-%m-%d'))
    elif duration == "3 Weeks":
        for i in range(21):  # 21 days for 3 weeks
            day = start_date + timedelta(days=i)
            dates.append(day.strftime('%Y-%m-%d'))
    elif duration == "1 Month":
        # Calculate dates for 1 month (approximately 30 days)
        for i in range(30):
            day = start_date + timedelta(days=i)
            dates.append(day.strftime('%Y-%m-%d'))
    return dates

# Streamlit app
st.title("AI-Fitness Planner")

st.sidebar.title("User Preferences")
name = st.sidebar.text_input("Name")
age = st.sidebar.number_input("Age", min_value=0, max_value=100)
experience_level = st.sidebar.selectbox("Experience Level", options=["Beginner", "Intermediate", "Advanced"])
target_body_part = st.sidebar.multiselect("Target Body Parts", options=df['BodyPart'].unique())
equipment_available = st.sidebar.multiselect("Equipment Available", options=df['Equipment'].unique())
duration = st.sidebar.selectbox("Plan Duration", options=["1 Week", "2 Weeks", "3 Weeks", "1 Month"])

start_date = st.sidebar.date_input("Starting Date", datetime.today())

if st.sidebar.button("Generate Plan"):
    with st.spinner('Generating plan...'):
        user_preferences = {
            "name": name,
            "age": age,
            "experience_level": experience_level,
            "target_body_part": target_body_part,
            "equipment_available": equipment_available
        }

        plan = generate_workout_plan(user_preferences, duration, start_date)
        if plan:
            st.subheader(f"Workout Plan for {duration}")
            st.write(plan)
            
            st.write("Starting Date: ", start_date.strftime('%Y-%m-%d'))
            dates = calculate_dates(duration, start_date)
            # st.write("Dates for the Plan:")
            # st.write(dates)

            # Add Save button to save plan to a file
            file_name = f"{name}_workout_plan.txt"  # Example file name
            plan_bytes = plan.encode('utf-8')
            st.download_button(label="Click here to download", data=plan_bytes, file_name=file_name, mime="text/plain")

            # st.write("Check the calendar page for an interactive calendar display.")
            # st.markdown(f"[View in Calendar](http://localhost:8501/calendar)")

