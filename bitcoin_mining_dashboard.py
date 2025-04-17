
import streamlit as st
import pandas as pd
import altair as alt
import os
import requests
import time

# Fetch live BTC price
@st.cache_data(ttl=60)
def fetch_btc_price():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
        response = requests.get(url)
        return response.json()["bitcoin"]["usd"]
    except:
        return 85000  # fallback price

# Sidebar config
st.set_page_config(page_title="Used Bitcoin Mining ROI Dashboard", layout="wide")
refresh_interval = st.sidebar.selectbox("🔁 Auto-Refresh Interval", [1, 5, 10], index=1)
st_autorefresh(interval=refresh_interval * 60 * 1000, key="refresh")
btc_price = fetch_btc_price()

# Header with live BTC price
st.title(f"📊 Used Bitcoin Mining ROI Dashboard")
st.subheader(f"💰 Live BTC Price: ${btc_price:,.2f} (auto-refreshes every {refresh_interval} min)")


import streamlit as st
import pandas as pd
import altair as alt
import os

st.set_page_config(page_title="Used Bitcoin Mining ROI Dashboard", layout="wide")
st.title("📊 Used Bitcoin Mining ROI Dashboard")

projection_file = "Bitcoin_Mining_Projection_DashboardUI.xlsx"
comparison_file = "Bitcoin_Mining_Comparison_WithHardwareCost.xlsx"

# Miner selector and view toggle
num_miners = st.sidebar.number_input("🔢 Number of Miners", min_value=1, max_value=100, value=10, step=1)
view_mode = st.sidebar.radio("📅 View Mode", ["Monthly", "Daily"])

tab1, tab2, tab3 = st.tabs(["S19j Pro (Used) ROI", "Compare Used Miners", "Setup Cost Details"])

with tab1:
    if os.path.exists(projection_file):
        try:
            df = pd.read_excel(projection_file, sheet_name="Sheet1", engine="openpyxl")
            monthly_df = pd.read_excel(projection_file, sheet_name="Monthly Summary", engine="openpyxl")

            # Scale by number of miners
            df_scaled = df.copy()
            for col in ["BTC Mined/Day", "Daily Revenue ($)", "Net Daily Revenue ($)", "Cumulative BTC", "Cumulative Revenue ($)", "Cumulative Net Revenue ($)", "Final Net Revenue ($)"]:
                if col in df_scaled.columns:
                    df_scaled[col] = df_scaled[col] * num_miners / 10

            monthly_df_scaled = monthly_df.copy()
            for col in ["Monthly Revenue ($)", "Monthly BTC Mined", "Cumulative Revenue ($)", "Cumulative BTC Mined"]:
                if col in monthly_df_scaled.columns:
                    monthly_df_scaled[col] = monthly_df_scaled[col] * num_miners / 10

            st.subheader("🔑 Key Metrics")
            col1, col2, col3 = st.columns(3)
            col1.metric("Total BTC Mined", f"{df_scaled['Cumulative BTC'].iloc[-1]:.4f} BTC")
            col2.metric("Final Net Revenue", f"${df_scaled['Final Net Revenue ($)'].iloc[-1]:,.2f}")
            breakeven_row = df_scaled[df_scaled['Final Net Revenue ($)'] > 0].iloc[0]
            col3.metric("ROI Breakeven Date", breakeven_row['Date'].strftime("%Y-%m-%d"))

            if view_mode == "Monthly":
                st.subheader("📈 Monthly Revenue")
                st.altair_chart(alt.Chart(monthly_df_scaled).mark_line(point=True).encode(
                    x='Month:T',
                    y='Monthly Revenue ($):Q'
                ).properties(width=800, height=300), use_container_width=True)

                st.subheader("🪙 Monthly BTC Mined")
                st.altair_chart(alt.Chart(monthly_df_scaled).mark_line(point=True, color="orange").encode(
                    x='Month:T',
                    y='Monthly BTC Mined:Q'
                ).properties(width=800, height=300), use_container_width=True)

                st.subheader("📋 Monthly Table")
                st.dataframe(monthly_df_scaled.style.format({
                    "Monthly Revenue ($)": "${:,.2f}",
                    "Monthly BTC Mined": "{:,.6f}",
                    "Cumulative Revenue ($)": "${:,.2f}",
                    "Cumulative BTC Mined": "{:,.6f}"
                }), use_container_width=True)

            else:
                st.subheader("📈 Daily Revenue")
                st.line_chart(df_scaled[["Date", "Net Daily Revenue ($)"]].set_index("Date"))

                st.subheader("🪙 Daily BTC Mined")
                st.line_chart(df_scaled[["Date", "BTC Mined/Day"]].set_index("Date"))

                st.subheader("📋 Daily Table")
                st.dataframe(df_scaled[["Date", "BTC Mined/Day", "Net Daily Revenue ($)", "Cumulative BTC", "Cumulative Revenue ($)"]].style.format({
                    "Net Daily Revenue ($)": "${:,.2f}",
                    "BTC Mined/Day": "{:,.6f}",
                    "Cumulative Revenue ($)": "${:,.2f}",
                    "Cumulative BTC": "{:,.6f}"
                }), use_container_width=True)

        except Exception as e:
            st.error(f"❌ Error loading Excel sheets from {projection_file}: {e}")
    else:
        st.warning(f"📁 File not found: {projection_file}. Please ensure it's in the same directory.")

# Skipping tab2 & tab3 for now to focus update on S19j Pro tab with miner count & view toggle



with tab2:
    if os.path.exists(comparison_file):
        try:
            st.header("📊 Compare Used Miners")
            models = ["S19j Pro", "S19 XP", "S21 Hydro"]
            for model in models:
                st.subheader(f"📈 {model} ROI")
                df_model = pd.read_excel(comparison_file, sheet_name=model, engine="openpyxl")
                df_model_scaled = df_model.copy()
                for col in ["BTC Mined/Day", "Net Daily Revenue ($)", "Cumulative Revenue ($)", "Cumulative BTC", "Final Net Revenue ($)"]:
                    if col in df_model_scaled.columns:
                        df_model_scaled[col] = df_model_scaled[col] * num_miners / 10
                df_model_scaled["Hardware Cost ($)"] = df_model["Hardware Cost ($)"] * num_miners / 10
                breakeven = df_model_scaled[df_model_scaled["Cumulative Revenue ($)"] > df_model_scaled["Hardware Cost ($)"].iloc[0]]

                col1, col2, col3 = st.columns(3)
                col1.metric("Total BTC Mined", f"{df_model_scaled['Cumulative BTC'].iloc[-1]:.4f} BTC")
                col2.metric("Final Net Revenue", f"${df_model_scaled['Final Net Revenue ($)'].iloc[-1]:,.2f}")
                if not breakeven.empty:
                    col3.metric("ROI Breakeven Date", breakeven.iloc[0]["Date"].strftime("%Y-%m-%d"))
                else:
                    col3.metric("ROI Breakeven Date", "Not Achieved")

                if view_mode == "Monthly":
                    df_model_scaled["Month"] = df_model_scaled["Date"].dt.to_period("M").dt.to_timestamp()
                    monthly_group = df_model_scaled.groupby("Month").agg({
                        "Net Daily Revenue ($)": "sum",
                        "BTC Mined/Day": "sum"
                    }).rename(columns={
                        "Net Daily Revenue ($)": "Monthly Revenue ($)",
                        "BTC Mined/Day": "Monthly BTC Mined"
                    }).reset_index()
                    monthly_group["Cumulative Revenue ($)"] = monthly_group["Monthly Revenue ($)"].cumsum()
                    monthly_group["Cumulative BTC Mined"] = monthly_group["Monthly BTC Mined"].cumsum()

                    st.altair_chart(alt.Chart(monthly_group).mark_line(point=True).encode(
                        x="Month:T", y="Monthly Revenue ($):Q"
                    ).properties(height=300), use_container_width=True)

                    st.dataframe(monthly_group.style.format({
                        "Monthly Revenue ($)": "${:,.2f}",
                        "Monthly BTC Mined": "{:,.6f}",
                        "Cumulative Revenue ($)": "${:,.2f}",
                        "Cumulative BTC Mined": "{:,.6f}"
                    }), use_container_width=True)
                else:
                    st.line_chart(df_model_scaled[["Date", "Net Daily Revenue ($)"]].set_index("Date"))
                    st.dataframe(df_model_scaled[["Date", "BTC Mined/Day", "Net Daily Revenue ($)", "Cumulative BTC", "Cumulative Revenue ($)"]].style.format({
                        "Net Daily Revenue ($)": "${:,.2f}",
                        "BTC Mined/Day": "{:,.6f}",
                        "Cumulative Revenue ($)": "${:,.2f}",
                        "Cumulative BTC": "{:,.6f}"
                    }), use_container_width=True)
        except Exception as e:
            st.error(f"❌ Error loading comparison file: {e}")

with tab3:
    st.markdown("""
### 💡 Setup Cost Breakdown

| Component                     | Description                                                                 | Estimated Cost |
|------------------------------|-----------------------------------------------------------------------------|----------------|
| ⚡ **Power Installation**     | 100 ft trench, 240V line to shed (includes conduit, wiring, labor)         | **$6,500**     |
| 🗄️ **Mining Rack**            | Heavy-duty vertical rack for 10 Antminers                                  | **$600**       |
| 🔌 **PDUs**                   | Industrial-grade Power Distribution Units (e.g., L6-30P, C13/C19 outlets)   | **$400**       |
| 🌬️ **Ventilation System**     | High-CFM intake/exhaust fans, ducting, filters                              | **$750**       |
| 🔇 **Soundproofing Materials**| Mineral wool, foam insulation, door seals                                  | **$450**       |

**Total Setup Cost: $8,700**
    """)

    st.subheader("📊 ROI Comparison Summary (10 Miners)")
    st.image("roi_bar_chart_scaled.png")

    st.subheader("⏱️ Payback Time to Breakeven (10 Miners)")
    st.image("payback_time_chart_scaled.png")
