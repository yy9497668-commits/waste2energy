
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


st.divider()
st.header("📊 Waste Analytics Dashboard")

try:
    response = supabase.table("waste_entries").select("*").execute()
    analytics_df = pd.DataFrame(response.data)

    if analytics_df.empty:
        st.info("No waste data available yet. Add a waste entry first.")
    else:
        analytics_df["weight_kg"] = pd.to_numeric(
            analytics_df["weight_kg"], errors="coerce"
        )
        analytics_df = analytics_df.dropna(subset=["weight_kg"])

        total_waste = analytics_df["weight_kg"].sum()
        total_entries = len(analytics_df)
        total_locations = analytics_df["location"].nunique()

        col1, col2, col3 = st.columns(3)

        col1.metric("♻️ Total Waste", f"{total_waste:,.2f} kg")
        col2.metric("📝 Total Entries", total_entries)
        col3.metric("📍 Locations", total_locations)

        st.subheader("Waste by Category")
        category_data = analytics_df.groupby(
            "category"
        )["weight_kg"].sum().sort_values(ascending=False)

        st.bar_chart(category_data)

        st.subheader("Waste by Location")
        location_data = analytics_df.groupby(
            "location"
        )["weight_kg"].sum().sort_values(ascending=False)

        st.bar_chart(location_data)

        if "waste_date" in analytics_df.columns:
            st.subheader("Waste Records Over Time")
            analytics_df["waste_date"] = pd.to_datetime(
                analytics_df["waste_date"], errors="coerce"
            )
            date_data = analytics_df.dropna(subset=["waste_date"])
            date_data = date_data.groupby(
                "waste_date"
            )["weight_kg"].sum().sort_index()

            if not date_data.empty:
                st.line_chart(date_data)

except Exception as e:
    st.error(f"Could not load analytics: {e}")

st.divider()
st.header("⚡ Waste-to-Energy Calculator")

st.write(
    "Estimate potential energy generation from the recorded waste. "
    "These are illustrative estimates, not measured electricity output."
)

energy_factors = {
    "Organic": 0.10,
    "Paper": 0.20,
    "Plastic": 0.70,
    "Metal": 0.00,
    "Glass": 0.00,
    "Other": 0.10
}

st.caption(
    "Illustrative factors only (kWh per kg). Actual output depends on "
    "waste composition, moisture, technology and conversion efficiency."
)

selected_category = st.selectbox(
    "Select Waste Category",
    list(energy_factors.keys())
)

weight_kg = st.number_input(
    "Enter Waste Weight (kg)",
    min_value=0.0,
    value=10.0,
    step=1.0
)

if st.button("Calculate Estimated Energy"):
    estimated_energy = weight_kg * energy_factors[selected_category]

    st.metric(
        "Estimated Energy Potential",
        f"{estimated_energy:.2f} kWh"
    )

    st.info(
        "This is a simplified illustrative estimate, not a guarantee "
        "of electricity that can actually be generated."
    )

st.divider()
st.header("⚡ Energy Analytics Dashboard")

# Illustrative estimates in kWh per kg.
# Replace these with verified factors for your chosen technology.
energy_factors = {
    "organic": 0.10,
    "paper": 0.20,
    "plastic": 0.70,
    "metal": 0.00,
    "other": 0.10
}

try:
    response = supabase.table("waste_entries").select("*").execute()
    energy_df = pd.DataFrame(response.data)

    if energy_df.empty:
        st.info("Add waste entries to see energy analytics.")
    else:
        energy_df["weight_kg"] = pd.to_numeric(
            energy_df["weight_kg"], errors="coerce"
        )
        energy_df = energy_df.dropna(subset=["weight_kg"])
        energy_df["category_key"] = (
            energy_df["category"].astype(str).str.strip().str.lower()
        )

        energy_df["factor_kwh_per_kg"] = (
            energy_df["category_key"].map(energy_factors)
        )

        energy_df["estimated_energy_kwh"] = (
            energy_df["weight_kg"] * energy_df["factor_kwh_per_kg"]
        )

        total_energy = energy_df["estimated_energy_kwh"].sum()
        known_df = energy_df.dropna(subset=["factor_kwh_per_kg"])

        col1, col2 = st.columns(2)
        col1.metric("Estimated Energy", f"{total_energy:,.2f} kWh")
        col2.metric(
            "Waste with Known Factors",
            f"{known_df['weight_kg'].sum():,.2f} kg"
        )

        st.subheader("Estimated Energy by Category")
        category_energy = known_df.groupby(
            "category"
        )["estimated_energy_kwh"].sum().sort_values(ascending=False)

        st.bar_chart(category_energy)

        st.subheader("Waste and Estimated Energy Records")
        st.dataframe(
            energy_df[
                [
                    "waste_date",
                    "location",
                    "category",
                    "weight_kg",
                    "estimated_energy_kwh"
                ]
            ],
            use_container_width=True
        )

        st.caption(
            "Energy values are illustrative estimates, not measured output. "
            "Actual energy depends on waste composition, moisture and "
            "conversion technology. Metal is assigned zero in this demo."
        )

except Exception as e:
    st.error(f"Could not load energy analytics: {e}")
