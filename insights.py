import streamlit as st
import json, os

RECORD_FILE = "record.json"


def loadData():
    with open(RECORD_FILE, "r") as file:
        data = json.load(file)

    return data

with st.line_chart()