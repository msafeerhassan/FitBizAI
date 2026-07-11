import streamlit as st
import os
from datetime import date
from db import loadFullRecordData

st.header("Progress Photos Timeline")

recordData = loadFullRecordData()

if not recordData:
    st.info("No data recorded yet - Nothing to show here :(")
    st.stop()

fortnightlyLogs = recordData.get("fortnightly", [])

if not fortnightlyLogs:
    st.info("No fortnightly logs found :(")
    st.stop()

def sortByDate(entry):
    return entry.get("date", "")

sortedData = sorted(fortnightlyLogs, key=sortByDate)

for cp in sortedData:
    cpDate = cp.get("date", "Unknown Date")
    cpWeight = cp.get("weight", "Unknown")
    imagePaths = cp.get("image_paths", [])

    st.markdown(f"### {cpDate} - {cpWeight} kg")

    validImagePaths = []

    for imagePath in imagePaths:
        if os.path.exists(imagePath):
            validImagePaths.append(imagePath)
        
    if validImagePaths:
        imageCols = st.columns(len(validImagePaths))

        for i in range(len(validImagePaths)):
            with imageCols[i]:
                st.image(validImagePaths[i])
    else:
        st.caption("Images missing :(")
    
    st.divider()