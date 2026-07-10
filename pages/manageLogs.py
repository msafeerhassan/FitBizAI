import streamlit as st
from datetime import date, time, datetime
from db import loadFullRecordData, saveFullRecordData

st.header("Manage Logs")

def getEarliestDate(data):
    earliestDate = None
    categories = ["diet", "water", "workout", "context", "productivity"]

    for category in categories:
        categoryRecords = data.get(category, [])

        for item in categoryRecords:
            itemDateStr = item.get("date", "")
            try:
                itemDate = date.fromisoformat(itemDateStr)
            except ValueError:
                continue

            if earliestDate is None:
                earliestDate = itemDate
            elif itemDate < earliestDate:
                earliestDate = itemDate
    
    return earliestDate

def sortEntries(categoryRecords, startDate, endDate):
    indexedEntries = []

    for i in range(len(categoryRecords)):
        entry = categoryRecords[i]
        entryDateStr = entry.get("date", "")

        try:
            entryDate = date.fromisoformat(entryDateStr)
        except ValueError:
            continue

        if entryDate >= startDate and entryDate <= endDate:
            indexedEntries.append((i, entry))
    
    def sortKey(indexedEntry):
        entry = indexedEntry[1]
        dateStr = entry.get("date", "")
        timeStr = entry.get("time", "")

        return dateStr + " " + timeStr

    indexedEntries.sort(key=sortKey, reverse=True)

    return indexedEntries

recordData = loadFullRecordData()

if not recordData:
    st.info("No Data recorded yet - nothing to manage here :(")
    st.stop()

if "editKey" not in st.session_state:
    st.session_state["editKey"] = None

st.markdown("### Filter by Date")

earliestDate = getEarliestDate(recordData)

if earliestDate is None:
    earliestDate = date.today()

filterCol1, filterCol2 = st.columns(2)

with filterCol1:
    startDate = st.date_input("From:", value=earliestDate)

with filterCol2:
    endDate = st.date_input("To:", value=date.today())

st.divider()

st.markdown("### Your Logs")

dietTab, waterTab, workoutTab, contextTab, productivityTab = st.tabs(
    [
        "Diet",
        "Water",
        "Workout",
        "Context",
        "Productivity"
    ]
)

with dietTab:
    dietRecords = recordData.get("diet", [])

    filteredDiet = sortEntries(dietRecords, startDate, endDate)

    if not filteredDiet:
        st.caption("No diet entries in this date range")

    for i, entry in filteredDiet:
        entryKey = "diet_" + str(i)

        listCol, editCol, deleteCol = st.columns([6, 1, 1])

        with listCol:
            st.write(f"**{entry.get('date')} {entry.get('time')}** - {entry.get('item')}")
        with editCol:
            editClicked = st.button("Edit", key="editbtn_" + entryKey)
            if editClicked:
                st.session_state["editKey"] = entryKey
        with deleteCol:
            deleteClicked = st.button("Delete", key="deleteBtn_" + entryKey)
            if deleteClicked:
                dietRecords.pop(i)
                saveFullRecordData(recordData)
                st.success("Entry deleted!")
                st.rerun()
        
        if st.session_state["editKey"] == entryKey:
            with st.form(key="editForm_" + entryKey):
                st.markdown("#### Edit Diet Entry")

                newDate = st.date_input("Date: ", value=date.fromisoformat(entry.get("date")))
                newTime = st.time_input("Time: ", value=time.fromisoformat(entry.get("time")))
                newItem = st.text_area("Item: ", value=entry.get("item"))

                saveBtn = st.form_submit_button("Save Changes")

            if saveBtn:
                dietRecords[i]["date"] = newDate.isoformat()
                dietRecords[i]["time"] = newTime.strftime("%H:%M:%S")
                dietRecords[i]["item"] = newItem

                saveFullRecordData(recordData)
                st.session_state["editKey"] = None
                st.success("Entry Updated")
                st.rerun()

with waterTab:
    waterRecords = recordData.get("water", [])
    filteredWater = sortEntries(waterRecords, startDate, endDate)

    if not filteredWater:
        st.caption("No water entries logged in this date range")
    
    for i, entry in filteredWater:
        entryKey = "water_" + str(i)

        listCol, editCol, deleteCol = st.columns([6,1,1])

        with listCol:
            st.write(f"**{entry.get('date')} {entry.get('time')}** - {entry.get('amount')} L")
        with editCol:
            editClicked = st.button("Edit", key="editbtn_" + entryKey)
            if editClicked:
                st.session_state["editKey"] = entryKey
        with deleteCol:
            deleteClicked = st.button("Delete", key="deleteBtn_" + entryKey)
            if deleteClicked:
                waterRecords.pop(i)
                saveFullRecordData(recordData)
                st.success("Entry Deleted!")
                st.rerun()
        
        if st.session_state["editKey"] == entryKey:
            with st.form(key="editForm_" + entryKey):
                st.markdown("#### Edit Water Entry")

                newDate = st.date_input("Date: ", value=date.fromisoformat(entry.get("date")))
                newTime = st.time_input("Time: ", value=time.fromisoformat(entry.get("time")))
                newAmount = st.number_input("Amount (Liters): ", value=float(entry.get("amount")), min_value=0.01)

                saveBtn = st.form_submit_button("Save Changes")
            if saveBtn:
                waterRecords[i]["date"] = newDate.isoformat()
                waterRecords[i]["time"] = newTime.strftime("%H:%M:%S")
                waterRecords[i]["amount"] = newAmount

                saveFullRecordData(recordData)

                st.session_state["editKey"] = None
                st.success("Entry Updated")
                st.rerun()

with workoutTab:
    workoutRecords = recordData.get("workout", [])
    filteredWorkout = sortEntries(workoutRecords, startDate, endDate)

    if not filteredWorkout:
        st.caption("No workout entries in this date range!")
    
    for i, entry in filteredWorkout:
        entryKey = "workout_" + str(i)

        listCol, editCol, deleteCol = st.columns([6,1,1])

        with listCol:
            st.write(f"**{entry.get('date')} {entry.get('time')}** - {entry.get('type')} ({entry.get('amount')})")
        with editCol:
            editClicked = st.button("Edit", key="editbtn_" + entryKey)

            if editClicked:
                st.session_state["editKey"] = entryKey
        
        with deleteCol:
            deleteClicked = st.button("Delete", key="deleteBtn_" + entryKey)
            if deleteClicked:
                workoutRecords.pop(i)
                saveFullRecordData(recordData)
                st.success("Entry Deleted!")
                st.rerun()
        
        if st.session_state["editKey"] == entryKey:
            with st.form(key="editForm_" + entryKey):
                st.markdown("#### Edit Workout Entry")

                newDate = st.date_input("Date: ", value=date.fromisoformat(entry.get("date")))
                newTime = st.time_input("Time: ", value=time.fromisoformat(entry.get("time")))
                newType = st.text_input("Workout Type: ", value=entry.get("type"))
                newAmount = st.number_input("Amount: ", value=int(entry.get("amount")), min_value=1)

                saveBtn = st.form_submit_button("Save Changes")
            if saveBtn:
                workoutRecords[i]["date"] = newDate.isoformat()
                workoutRecords[i]["time"] = newTime.strftime("%H:%M:%S")
                workoutRecords[i]["type"] = newType
                workoutRecords[i]["amount"] = newAmount

                saveFullRecordData(recordData)
                st.session_state["editKey"] = None
                st.success("Entry Updated!")
                st.rerun()