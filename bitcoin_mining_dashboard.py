
import streamlit as st
import pandas as pd
import requests
import os

@st.cache_data(ttl=60)
def fetch_btc_price():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
        return requests.get(url).json()["bitcoin"]["usd"]
    except:
        return 85000

# Files
projection_file = "Bitcoin_Mining_Projection_DashboardUI.xlsx"
comparison_file = "Bitcoin_Mining_Comparison_WithHardwareCost.xlsx"

# UI
st.set_page_config(page_title="Bitcoin Mining ROI Dashboard", layout="wide")
btc_price = fetch_btc_price()
refresh = st.sidebar.selectbox("Refresh BTC Price (min)", [1, 5, 10], index=1)
num_miners = st.sidebar.number_input("Number of Miners", 1, 100, value=10)
years = st.sidebar.selectbox("Project Duration (Years)", [1, 2, 3, 4, 5], index=2)

st.title("Bitcoin Mining ROI Dashboard")
st.subheader(f"Live BTC Price: ${btc_price:,.2f}")

tab0, tab1, tab2, tab3 = st.tabs(["Overview", "S19j Pro ROI", "Miner Comparison", "Setup Cost"])

with tab0:
    st.markdown("""
## 🏗️ Project Overview

Explore mining profitability of used Bitmain miners (S19j Pro, S19 XP, S21 Hydro) with configurable BTC trends, number of miners, and project duration.
    """)

with tab1:
    trend = st.radio("BTC Price Trend", ["Bullish", "Bearish"], index=0)
    suffix = "_Bullish" if trend == "Bullish" else "_Bearish"
    sheet1 = f"Sheet1{suffix}"
    summary = f"Monthly{suffix}"
    if os.path.exists(projection_file):
        df = pd.read_excel(projection_file, sheet_name=sheet1)
        monthly_df = pd.read_excel(projection_file, sheet_name=summary)
        df = df.head(years * 365)
        monthly_df = monthly_df.head(years * 12)

        df_scaled = df.copy()
        monthly_scaled = monthly_df.copy()
        for col in ["BTC Mined/Day", "Net Daily Revenue ($)", "Cumulative BTC", "Cumulative Net Revenue ($)", "Final Net Revenue ($)"]:
            df_scaled[col] *= num_miners / 10
        for col in ["Monthly Revenue ($)", "Monthly BTC Mined", "Cumulative Revenue ($)", "Cumulative BTC Mined"]:
            monthly_scaled[col] *= num_miners / 10

        st.subheader("Key Metrics")
        col0, col1, col2, col3 = st.columns(4)
        col0.metric("Project Duration", f"{years} years")
        col1.metric("Total BTC Mined", f"{df_scaled['Cumulative BTC'].iloc[-1]:.4f}")
        col2.metric("Final Net Revenue", f"${df_scaled['Final Net Revenue ($)'].iloc[-1]:,.2f}")
        roi = df_scaled[df_scaled["Final Net Revenue ($)"] > 0]
        col3.metric("Breakeven", roi.iloc[0]["Date"].strftime("%Y-%m-%d") if not roi.empty else "Not Achieved")

        st.line_chart(monthly_scaled.set_index("Month")[["Monthly Revenue ($)"]])
        st.line_chart(monthly_scaled.set_index("Month")[["Monthly BTC Mined"]])
        columns_to_show = [c for c in ["Date", "BTC Mined/Day", "BTC Price ($)", "Net Daily Revenue ($)", "Cumulative BTC", "Cumulative Net Revenue ($)"] if c in df_scaled.columns]
        st.dataframe(df_scaled[columns_to_show])

with tab2:
    if os.path.exists(comparison_file):
        for model in ["S19j Pro", "S19 XP", "S21 Hydro"]:
            st.subheader(f"{model}")
            df = pd.read_excel(comparison_file, sheet_name=model).head(years * 365)
            df_scaled = df.copy()
            for col in ["BTC Mined/Day", "Net Daily Revenue ($)", "Cumulative Revenue ($)", "Cumulative BTC", "Final Net Revenue ($)"]:
                df_scaled[col] *= num_miners / 10
            cost = df["Hardware Cost ($)"].iloc[0] * num_miners / 10
            roi = df_scaled[df_scaled["Cumulative Revenue ($)"] > cost]

            c0, c1, c2, c3, c4 = st.columns(5)
            c0.metric("Duration", f"{years} yrs")
            c1.metric("Cost", f"${cost:,.0f}")
            c2.metric("BTC Mined", f"{df_scaled['Cumulative BTC'].iloc[-1]:.4f}")
            c3.metric("Net Revenue", f"${df_scaled['Final Net Revenue ($)'].iloc[-1]:,.2f}")
            c4.metric("Breakeven", roi.iloc[0]["Date"].strftime("%Y-%m-%d") if not roi.empty else "Not Achieved")

            st.line_chart(df_scaled.set_index("Date")[["Net Daily Revenue ($)"]])

with tab3:
    st.markdown("""
### Setup Cost Breakdown

| Component            | Description                             | Cost   |
|---------------------|-----------------------------------------|--------|
| ⚡ Power Line        | 100 ft trench + 240V wiring             | $6,500 |
| 🗄️ Rack              | Rack for 10 miners                      | $600   |
| 🔌 PDUs              | 30A power units                         | $400   |
| 🌬️ Ventilation       | Intake + exhaust fan setup              | $750   |
| 🔇 Soundproofing     | Foam, seals, noise reduction            | $450   |

**Total: $8,700**
    """)
    st.image("roi_bar_chart_scaled.png")
    st.image("payback_time_chart_scaled.png")
