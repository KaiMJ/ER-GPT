import json
import streamlit as st
import time
from model import ER_GPT
from dotenv import load_dotenv
import os
from model import ER_GPT
from PIL import Image
import time
import openai

max_attempt = 5
load_dotenv()
sideb = st.sidebar
OPENAPI_KEY = sideb.text_input(
    "Input your Open AI API key", value=os.getenv("OPENAPI_KEY")
)
openai.api_key = OPENAPI_KEY
submitted = st.sidebar.button("Submit")


def is_api_key_valid():
    try:
        with st.spinner("Checking API key..."):
            response = openai.Completion.create(
                engine="davinci", prompt="Test", max_tokens=1
            )
            with open("default_state.json", "r") as source_file:
                source_data = json.load(source_file)
            with open("states.json", "w") as destination_file:
                json.dump(source_data, destination_file)
            return True
    except:
        return False


if submitted:
    if is_api_key_valid():
        st.sidebar.success("API key is valid")
    else:
        st.sidebar.error("API key is invalid")

model = ER_GPT()

states = json.load(open("states.json", "r"))

user_input = st.text_input(states["input_prompt"], key="input")


def click_confirm():
    # Need to set state to next_run
    if states["next_run"]:
        print("This should be edit")

        with st.spinner("Editing diagram..."):
            done = False
            print(f"Attempt {states['attempt']}: Editing diagram")

            while not done and states["attempt"] < max_attempt:
                try:
                    edit_result = model.step_4(
                        st.session_state["input"], states["code"]
                    )
                    done = True
                except Exception as e:
                    print(e)
                    states["attempt"] += 1
                    with open("states.json", "w") as f:
                        json.dump(states, f)

            if not done:
                st.error("Model failed to edit diagram. Please rerun")
            else:
                states["code"] = edit_result

        states["attempt"] = 0

    else:
        print("This should be first run")
        states["input_prompt"] = "Edit the Enterprise Architecture diagram"

        with st.spinner("Generating diagram..."):
            done = False

            while not done and states["attempt"] < max_attempt:
                print(f"Attempt {states['attempt']}: Generating diagram")
                try:
                    architecture_result = model.step_1(st.session_state["input"])
                    diagram_result = model.step_2(architecture_result)
                    code_result = model.step_3(diagram_result)
                    done = True
                except Exception as e:
                    print(e)
                    states["attempt"] += 1
                    with open("states.json", "w") as f:
                        json.dump(states, f)

            if not done:
                st.error("Model failed to edit diagram. Please rerun")
            else:
                states["code"] = code_result

        states["attempt"] = 0

    states["next_run"] = True
    with open("states.json", "w") as f:
        json.dump(states, f)
    st.session_state["input"] = ""


def click_reset():
    st.session_state["input"] = ""
    states["next_run"] = False
    states["code"] = ""
    states["input_prompt"] = "Generate an Enterprise Architecture diagram"
    states["attempt"] = 0

    with open("states.json", "w") as f:
        json.dump(states, f)


st.button("Confirm", on_click=click_confirm)
if states["next_run"]:
    if states["code"] != "":
        st.image(Image.open("diagram.png"), width=600)
    st.button("Reset", on_click=click_reset)
