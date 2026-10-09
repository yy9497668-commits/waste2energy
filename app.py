
import streamlit as st
import pandas as pd
from supabase import create_client

st.set_page_config(
    page_title="Waste2Energy",
    page_icon="♻️",
    layout="wide"
)

st.title("♻️ Waste2Energy")
st.write("Smart Waste Management & Energy Analytics")

# Connect to Supabase using Streamlit Secrets

@st.cache_resource
def get_supabase_client():
    url = st.secrets["SUPABASE_URL"].strip().rstrip("/")
    st.write("Supabase URL format:", url.startswith("https://"),
             url.endswith(".supabase.co"))
    return create_client(
        url,
        st.secrets["SUPABASE_KEY"].strip()
    )

try:
    supabase = get_supabase_client()
except Exception:
    st.error(
        "Database connection failed. Please check your "
        "Streamlit Secrets settings."
    )
    st.stop()


def load_data():
    result = (
        supabase.table("waste_entries")
        .select("*")
        .order("waste_date", desc=True)
        .execute()
    )
    return pd.DataFrame(result.data)


page = st.sidebar.radio(
    "Choose Page",
    ["Dashboard", "Add Waste", "View Data"]
)

if page == "Add Waste":
    st.subheader("Add a Waste Entry")

    with st.form("waste_form"):
        waste_date = st.date_input("Date")
        location = st.text_input("Location")

        category = st.selectbox(
            "Waste Category",
            ["Organic", "Paper", "Plastic", "Metal", "Other"]
        )

        weight = st.number_input(
            "Weight (kg)",
            min_value=0.0,
            step=0.5
        )

        submitted = st.form_submit_button("Save Waste Entry")

        if submitted:
            if not location.strip() or weight <= 0:
                st.warning(
                    "Enter a location and a weight greater than zero."
                )
            else:
                try:
                    supabase.table("waste_entries").insert({
                        "waste_date": waste_date.isoformat(),
                        "location": location.strip(),
                        "category": category,
                        "weight_kg": weight
                    }).execute()

                    st.success("Entry saved to the database!")
                    st.rerun()

            
                except Exception as e:
                    st.error(f"Database error: {e}")

elif page == "Dashboard":
    st.subheader("Waste Dashboard")

    try:
        df = load_data()

        if df.empty:
            st.info("No waste records yet. Add your first entry!")
        else:
            total_waste = df["weight_kg"].sum()
            organic_waste = df.loc[
                df["category"] == "Organic", "weight_kg"
            ].sum()

            col1, col2 = st.columns(2)
            col1.metric("Total Waste (kg)", f"{total_waste:.2f}")
            col2.metric("Organic Waste (kg)", f"{organic_waste:.2f}")

            category_totals = (
                df.groupby("category")["weight_kg"].sum()
            )

            st.subheader("Waste by Category")
            st.bar_chart(category_totals)

        st.caption(
            "Energy estimates are not included until a validated "
            "conversion factor is selected."
        )

    except Exception:
        st.error("Could not load dashboard data from the database.")

elif page == "View Data":
    st.subheader("Waste Records")

    try:
        df = load_data()

        if df.empty:
            st.info("No records available yet.")
        else:
            st.dataframe(df, use_container_width=True)

            st.download_button(
                "Download CSV",
                df.to_csv(index=False),
                "waste_data.csv",
                "text/csv"
            )

    except Exception:
        st.error("Could not retrieve records from the database.")
