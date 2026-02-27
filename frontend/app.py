import streamlit as st
import requests
import pandas as pd
import mysql.connector
import plotly.express as px

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Smart Packaging Optimizer",
    page_icon="📦",
    layout="wide"
)

st.title("📦 Smart Packaging Optimizer Dashboard")

st.markdown("""
### 🚀 AI-Based Smart Packaging Size Optimizer  
Reducing retail packaging waste, cost, and carbon emissions using intelligent box selection.
""")

# ---------------- FETCH DATA FUNCTION ----------------
def fetch_data():
    conn = mysql.connector.connect(
        host="localhost",
        user="packaging_user",
        password="Pack@123",
        database="smart_packaging"
    )
    df = pd.read_sql("SELECT * FROM shipments", conn)
    conn.close()
    return df

# ---------------- INPUT SECTION ----------------
st.subheader("📦 Optimize New Shipment")

length = st.number_input("Length (cm)")
width = st.number_input("Width (cm)")
height = st.number_input("Height (cm)")
weight = st.number_input("Weight (kg)")
fragile = st.checkbox("Fragile")

if st.button("Optimize Packaging"):

    try:
        response = requests.post(
            "http://127.0.0.1:8000/optimize",
            json={
                "length": length,
                "width": width,
                "height": height,
                "weight": weight,
                "fragile": fragile
            }
        )

        result = response.json()

        opt = result["optimization"]
        carbon = result["carbon_analysis"]

        st.success("✅ Packaging Optimized Successfully!")

        col1, col2 = st.columns(2)

        col1.metric("Recommended Box", opt["selected_box"])
        col1.metric("Waste %", f"{opt['waste_percentage']}%")

        col2.metric("CO2 Saved (kg)", carbon["co2_saved_kg"])
        col2.metric("Cost Saved", f"₹ {carbon['cost_saved']}")

        score = carbon["sustainability_score"]

        if score > 70:
            st.success("🌱 Excellent Sustainability Score!")
        elif score > 40:
            st.info("♻ Moderate Sustainability Score")
        else:
            st.warning("⚠ Low Sustainability Score")

    except:
        st.error("⚠ Backend not running. Start FastAPI server.")

# ---------------- ANALYTICS SECTION ----------------
st.subheader("📊 Analytics Dashboard")

df = fetch_data()

if not df.empty:

    total_shipments = len(df)
    total_co2 = df["co2_saved"].sum()
    total_cost = df["cost_saved"].sum()
    avg_waste = df["waste_percentage"].mean()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Shipments", total_shipments)
    col2.metric("Total CO2 Saved (kg)", round(total_co2, 2))
    col3.metric("Total Cost Saved", round(total_cost, 2))
    col4.metric("Avg Waste %", round(avg_waste, 2))

    st.markdown("---")

    fig1 = px.line(
        df,
        x="created_at",
        y="co2_saved",
        title="🌍 CO2 Saved Over Time",
        markers=True
    )
    st.plotly_chart(fig1, use_container_width=True)

    box_counts = df["selected_box"].value_counts().reset_index()
    box_counts.columns = ["Box", "Count"]

    fig2 = px.pie(
        box_counts,
        names="Box",
        values="Count",
        title="📦 Box Usage Distribution"
    )
    st.plotly_chart(fig2, use_container_width=True)

else:
    st.info("No shipment data available yet.")