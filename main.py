# Import the required libraries
import streamlit as st
from streamlit_pills import pills
import openai
import json
from dotenv import load_dotenv
import os
from model import ER_GPT
from PIL import Image
import time

load_dotenv()
sideb = st.sidebar
OPENAPI_KEY = sideb.text_input(
    "Input your Open AI API key", value=os.getenv("OPENAPI_KEY")
)

openai.api_key = OPENAPI_KEY

# submit button
submitted = st.sidebar.button("Submit")


def is_api_key_valid():
    try:
        response = openai.Completion.create(
            engine="davinci", prompt="Test", max_tokens=1
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


prompt = "You are a friendly chatbot."


# Create a title and a header
col1, col2 = st.columns((1, 4))

col1.image("ER_logo.png", caption="", width=100)
col2.title("ER Diagram Generator")


def main():
    model = ER_GPT()

    original_instruction = "Generate an ER diagram"
    user_input = st.text_input(original_instruction)

    st.markdown("----")

    def run_model(user_input):
        try:
            with st.spinner("Generating diagram..."):
                architecture_result = model.step_1(user_input)
                diagram_result = model.step_2(architecture_result)
                model.step_3(diagram_result)
                return True
        except Exception as e:
            print(e)
            return False

    if user_input:
        done = False
        attempts = 0
        while not done and attempts < 5:
            print("Attempt {}".format(attempts), end="\r")
            done = run_model(user_input)
            attempts += 1

        if not done:
            st.error("Model failed to generate an ER diagram")
            return False

        st.image(Image.open("diagram.png"), width=600)

        m = st.markdown(
            """
        <style>
        div.stButton > button:first-child {
            background-color: #FF6240;
        }
        div.stButton > button:hover {
            background-color: #FF2D00;
            color: #FFFFFF;
            }
        </style>""",
            unsafe_allow_html=True,
        )


main()
