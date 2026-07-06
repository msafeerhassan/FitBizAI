import streamlit as st
from db import saveData
import os, datetime

UPLOAD_FOLDER = "uploads"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

with st.form(key="fortnightlyLog", clear_on_submit=True, border=False):
    st.header("Fortnightly Log")

    images = st.file_uploader("Upload your Facial Images", type=["jpg", "png", "jpeg"], accept_multiple_files=True)
    
    weight = st.number_input("Enter your current weight (in kg's): ")

    submitBtn = st.form_submit_button("Submit Fortnightly Report")

if submitBtn:
    if len(images) < 3:
        st.error("Please upload atleast 3 images!")
    elif weight <= 10.0:
        st.error("Please enter a valid weight value.")
    else:
        savedImagePaths = []
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        for i, file in enumerate(images):
            fileExt = os.path.splitext(file.name)[1]
            fileName = f"face_{timestamp}_{i}{fileExt}"
            filePath = os.path.join(UPLOAD_FOLDER, fileName)

            with open(filePath, 'wb') as f:
                f.write(file.getbuffer())
            savedImagePaths.append(filePath)
        
        data = {
            "date": datetime.date.today().isoformat(),
            "weight": weight,
            "image_paths": savedImagePaths
        }

        saveData("fortnightly", data)
        st.success("Fortnightly Report Logged! Refresh to access whole application :)")