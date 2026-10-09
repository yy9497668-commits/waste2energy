import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="Waste2Energy", page_icon="♻️")

st.title("♻️ Waste2Energy")
st.write("Smart Waste Management & Energy Analytics")

file = Path("waste_data.csv")

if file.exists():
    df = pd.read_csv(file)
else:
    df = pd.DataFrame(
        columns=["Date", "Location", "Category", "Weight (kg)"]
    )

page = st.sidebar.radio(
    "Choose Page",
    ["Dashboard", "Add Waste", "View Data"]
)

if page == "Dashboard":
    st.subheader("Waste Dashboard")
    st.metric("Total Waste (kg)", round(df["Weight (kg)"].sum(), 2))
    st.bar_chart(df.groupby("Category")["Weight (kg)"].sum())

elif page == "Add Waste":
    with st.form("waste_form"):
        date = st.date_input("Date")
        location = st.text_input("Location")
        category = st.selectbox(
            "Waste Category",
            ["Organic", "Paper", "Plastic", "Metal", "Other"]
        )
        weight = st.number_input("Weight (kg)", min_value=0.0)
        submitted = st.form_submit_button("Save Waste Entry")

        if submitted:
            if not location.strip() or weight <= 0:
                st.warning("Enter a location and weight greater than zero.")
            else:
                new_row = pd.DataFrame([{
                    "Date": str(date),
                    "Location": location,
                    "Category": category,
                    "Weight (kg)": weight
                }])
                df = pd.concat([df, new_row], ignore_index=True)
                df.to_csv(file, index=False)
                st.success("Waste entry saved!")

elif page == "View Data":
    st.subheader("Waste Records")
    st.dataframe(df, use_container_width=True)
    st.download_button(
        "Download CSV",
        df.to_csv(index=False),
        "waste_data.csv",
        "text/csv"
    )
