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

# ---------------- INVENTORY FUNCTIONS ----------------
def fetch_inventory():
    try:
        resp = requests.get("http://127.0.0.1:8000/inventory", timeout=5)
        data = resp.json().get("inventory", [])
        return pd.DataFrame(data)
    except Exception:
        return pd.DataFrame(columns=["box_size", "stock", "usage_count"])


def update_inventory(box_size: str, change: int):
    try:
        requests.post(
            "http://127.0.0.1:8000/inventory/update",
            params={"box_size": box_size, "change": change},
            timeout=5
        )
    except Exception:
        st.error("Failed to update inventory. Is backend running?")

# sidebar controls
with st.sidebar:
    st.header("Controls")
    st.write("Use the tabs above to navigate between modules.")
    # additional filters can go here (date range, category, etc.)

# create tabs layout
tab1, tab2, tab3 = st.tabs(["Optimize", "Inventory", "Analytics"])

# ---------------- INPUT/OPTIMIZATION TAB ----------------
with tab1:
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

# ---------------- INVENTORY TAB ----------------
with tab2:
    st.subheader("📦 Packaging Inventory")
    inv_df = fetch_inventory()
    if inv_df.empty:
        st.info("Inventory data not available yet.")
    else:
        st.dataframe(inv_df)

    st.markdown("---")
    st.write("### Adjust Stock")
    col_a, col_b = st.columns(2)
    with col_a:
        box_input = st.text_input("Box Size")
    with col_b:
        qty_input = st.number_input("Change (use negative to reduce)", value=0)
    if st.button("Update Inventory"):
        if box_input and qty_input != 0:
            update_inventory(box_input, int(qty_input))
            st.success("Inventory updated, refresh the tab to see changes.")
        else:
            st.warning("Enter box size and non-zero change.")

# ---------------- ANALYTICS TAB ----------------
with tab3:
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

        # demand forecasting section
        st.markdown("### 📈 Demand Forecast")
        try:
            resp = requests.get("http://127.0.0.1:8000/forecast", timeout=5)
            fc = resp.json()
            if "error" in fc:
                st.warning(fc["error"])
            else:
                st.metric("Predicted shipments next week", fc.get("overall_next_week", 0))
                by_box = fc.get("by_box", {})
                if by_box:
                    df_pred = pd.DataFrame(list(by_box.items()), columns=["Box", "Predicted"])
                    st.table(df_pred)
                # plot history with predicted point
                hist = fc.get("history", [])
                if hist:
                    weeks = list(range(1, len(hist) + 1))
                    fig3 = px.line(x=weeks, y=hist, title="Weekly Shipments History", markers=True)
                    # add predicted point
                    fig3.add_scatter(x=[len(hist)+1], y=[fc.get("overall_next_week", 0)], mode='markers', name='Forecast')
                    st.plotly_chart(fig3, use_container_width=True)
        except Exception:
            st.warning("Forecast service unavailable")

    else:
        st.info("No shipment data available yet.")