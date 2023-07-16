# Import the required libraries
import streamlit as st
from streamlit_pills import pills
import openai
import json
from dotenv import load_dotenv
import os

load_dotenv()
sideb = st.sidebar
OPENAPI_KEY = sideb.text_input("Input your Open AI API key", value=os.getenv("OPENAPI_KEY"))

openai.api_key = OPENAPI_KEY

# submit button
submitted = st.sidebar.button("Submit")
def is_api_key_valid():
    try:
        response = openai.Completion.create(
            engine="davinci",
            prompt="Test",
            max_tokens=1
        )
    except:
        return False
    else:
        return True
    
if submitted:
    if is_api_key_valid():
        st.sidebar.success("API key is valid")
    else:
        st.sidebar.error("API key is invalid")


prompt = "Write me a 100 word essay why we are going to win this hackathon."

def gpt_response(message):
    result = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
                {"role": "user", "content": prompt},
                {"role": "assistant", "content": message},
            ]
    )
    return result.choices[0].message.content
    # return result

# Create a title and a header
col1, col2 = st.columns((1, 4))

col1.image("ER_logo.png", caption="", width=100)
col2.title("ER Diagram Generator")

user_input = st.text_input("Input any text to generate a ER diagram")

st.markdown("----")



if user_input:
    res_box = st.empty()

    report = []
    for resp in gpt_response(user_input):
        report.append(resp)
        result = "".join(report).strip()
        result = result.replace("\n", "")        
        res_box.markdown(f'*{result}*')
