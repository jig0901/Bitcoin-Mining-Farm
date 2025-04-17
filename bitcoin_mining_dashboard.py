
import streamlit as st
import pandas as pd
import altair as alt
import os
import requests

# Fetch live BTC price
@st.cache_data(ttl=60)
def fetch_btc_price():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
        response = requests.get(url)
        return response.json()["bitcoin"]["usd"]
    except:
        return 85000

projection_file = "Bitcoin_Mining_Projection_DashboardUI.xlsx"
comparison_file = "Bitcoin_Mining_Comparison_WithHardwareCost.xlsx"

# UI setup
st.set_page_config(page_title="Bitcoin Mining ROI Dashboard", layout="wide")
refresh_interval = st.sidebar.selectbox("🔁 Refresh BTC Price Every", [1, 5, 10], index=1)
btc_price = fetch_btc_price()
num_miners = st.sidebar.number_input("🔢 Number of Miners", min_value=1, max_value=100, value=10)

st.title("📊 Bitcoin Mining ROI Dashboard")
st.subheader(f"💰 Live BTC Price: ${btc_price:,.2f} (auto-refresh: {refresh_interval} min)")

tab0, tab1, tab2, tab3 = st.tabs(["Project Overview", "S19j Pro (Used) ROI", "Compare Used Miners", "Setup Cost Details"])

with tab0:
    st.markdown("""
## 🏗️ Project Overview

Welcome to the **Bitcoin Mining ROI Dashboard** — a live and interactive view into mining profitability using **used Bitmain S19-series miners**. This tool helps small-scale miners:

- 📈 Evaluate daily/monthly revenue
- ⚙️ Compare miner models (S19j Pro, S19 XP, S21 Hydro)
- 💰 Account for setup cost and breakeven
- 🔢 Simulate different numbers of miners
- 🔄 Track profitability based on live BTC price

Use the tabs above to explore detailed ROI calculations and charts.
    """)


with tab1:
    btc_trend = st.radio("📈 Bitcoin Price Trend", ["Bullish", "Bearish"], index=0)
    trend_suffix = "_Bullish" if btc_trend == "Bullish" else "_Bearish"
    sheet1 = f"Sheet1{trend_suffix}"
    summary = f"Monthly{trend_suffix}"

    if os.path.exists(projection_file):
        df = pd.read_excel(projection_file, sheet_name=sheet1, engine="openpyxl")
        monthly_df = pd.read_excel(projection_file, sheet_name=summary, engine="openpyxl")

        scale_factor = num_miners / 10
        for col in ["BTC Mined/Day", "Daily Revenue ($)", "Net Daily Revenue ($)", "Cumulative BTC", "Cumulative Net Revenue ($)", "Final Net Revenue ($)"]:
            if col in df.columns:
                df[col] *= scale_factor
        for col in ["Monthly Revenue ($)", "Monthly BTC Mined", "Cumulative Revenue ($)", "Cumulative BTC Mined"]:
            if col in monthly_df.columns:
                monthly_df[col] *= scale_factor

        st.subheader("🔑 Key Metrics")
        col0, col1, col2, col3 = st.columns(4)
                    col0, col1, col2, col3 = st.columns(4)
            col0.metric("Hardware Cost", f"${df_model_scaled['Hardware Cost ($)'].iloc[0]:,.2f}")
            col1.metric("Total BTC Mined", f"{df['Cumulative BTC'].iloc[-1]:.4f} BTC")
        col2.metric("Final Net Revenue", f"${df['Final Net Revenue ($)'].iloc[-1]:,.2f}")
        breakeven = df[df['Final Net Revenue ($)'] > 0]
        if not breakeven.empty:
            col3.metric("ROI Breakeven", breakeven.iloc[0]["Date"].strftime("%Y-%m-%d"))
        else:
            col3.metric("ROI Breakeven", "Not Achieved")

        st.subheader("📊 Monthly Revenue")
        st.line_chart(monthly_df.set_index("Month")[["Monthly Revenue ($)"]])
        st.subheader("📊 Monthly BTC Mined")
        st.line_chart(monthly_df.set_index("Month")[["Monthly BTC Mined"]])
        st.subheader("📋 Monthly Projection Table")
        st.dataframe(monthly_df.style.format({
            "Monthly Revenue ($)": "${:,.2f}",
            "Monthly BTC Mined": "{:,.6f}",
            "Cumulative Revenue ($)": "${:,.2f}",
            "Cumulative BTC Mined": "{:,.6f}"
        }), use_container_width=True)

with tab2:
    if os.path.exists(comparison_file):
        models = ["S19j Pro", "S19 XP", "S21 Hydro"]
        for model in models:
            st.subheader(f"📈 {model}")
            df_model = pd.read_excel(comparison_file, sheet_name=model, engine="openpyxl")
            df_model_scaled = df_model.copy()
            for col in ["BTC Mined/Day", "Net Daily Revenue ($)", "Cumulative Revenue ($)", "Cumulative BTC", "Final Net Revenue ($)"]:
                if col in df_model_scaled.columns:
                    df_model_scaled[col] = df_model_scaled[col] * num_miners / 10
            df_model_scaled["Hardware Cost ($)"] = df_model["Hardware Cost ($)"] * num_miners / 10
            breakeven = df_model_scaled[df_model_scaled["Cumulative Revenue ($)"] > df_model_scaled["Hardware Cost ($)"].iloc[0]]

            if not breakeven.empty:
            else:

        st.line_chart(df_model_scaled[["Date", "Net Daily Revenue ($)"]].set_index("Date"))

        col0, col1, col2, col3 = st.columns(4)
        col0.metric("Hardware Cost", f"${df_model_scaled['Hardware Cost ($)'].iloc[0]:,.2f}")
        col1.metric("Total BTC Mined", f"{df_model_scaled['Cumulative BTC'].iloc[-1]:.4f} BTC")
        col2.metric("Final Net Revenue", f"${df_model_scaled['Final Net Revenue ($)'].iloc[-1]:,.2f}")
        if not breakeven.empty:
            col3.metric("Breakeven Date", breakeven.iloc[0]["Date"].strftime("%Y-%m-%d"))
        else:
            col3.metric("Breakeven Date", "Not Achieved")
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
