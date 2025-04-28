
import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta

# Live BTC price fetch
@st.cache_data(ttl=60)
def fetch_btc_price():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
        return requests.get(url).json()["bitcoin"]["usd"]
    except:
        return 85000

# Simulation of projection dynamically based on current BTC price
def simulate_projection(base_price, growth_rate, days):
    pool_fee = 0.015
    difficulty_decline = 0.03
    data = []
    btc_price = base_price
    # per-miner rate for S19j Pro: ~0.0000519 BTC/day
    btc_per_day = 0.0000519 * 10
    for day in range(days):
        if day > 0 and day % 180 == 0:
            btc_price *= (1 + growth_rate)
        if day > 0 and day % 30 == 0:
            btc_per_day *= (1 - difficulty_decline)
        gross = btc_per_day * btc_price
        net = gross * (1 - pool_fee)
        data.append({
            "Date": datetime.today() + timedelta(days=day),
            "BTC Mined/Day": btc_per_day,
            "BTC Price ($)": btc_price,
            "Net Daily Revenue ($)": net
        })
    df = pd.DataFrame(data)
    df["Cumulative BTC"] = df["BTC Mined/Day"].cumsum()
    df["Cumulative Net Revenue ($)"] = df["Net Daily Revenue ($)"].cumsum()
    df["Final Net Revenue ($)"] = df["Cumulative Net Revenue ($)"] - 6500 - 600 - 400 - 750 - 450
    df["Month"] = df["Date"].dt.to_period("M").dt.to_timestamp()
    return df

# UI Setup
st.set_page_config(page_title="Bitcoin Mining ROI Dashboard", layout="wide")
btc_price = fetch_btc_price()
refresh = st.sidebar.selectbox("🔁 Refresh BTC Price (min)", [1,5,10], index=1)
num_miners = st.sidebar.number_input("🔢 Number of Miners", 1, 100, value=10)
years = st.sidebar.selectbox("🗓️ Project Duration (Years)", [1,2,3,4,5], index=2)
view_mode = st.sidebar.radio("📅 View Mode", ["Monthly","Daily"], index=0)
trend = st.sidebar.radio("📈 BTC Price Trend", ["Bullish","Bearish"], index=0)

st.title("📊 Bitcoin Mining ROI Dashboard")
st.subheader(f"💰 Live BTC Price: ${btc_price:,.2f}")

# Tabs
tab0, tab1, tab2, tab3 = st.tabs(["Overview","S19j Pro ROI","Miner Comparison","Setup Cost"])

with tab0:
    st.markdown("""
## 🏗️ Project Overview

This dashboard uses the **current BTC price** to dynamically project revenue and ROI for a set of used Bitmain miners. Adjust:
- Number of miners
- Project duration
- Price trend (Bullish/Bearish)
- View mode (Monthly/Daily)
    """)

with tab1:
    growth = 0.10 if trend=="Bullish" else -0.05
    days = years * 365
    df = simulate_projection(btc_price, growth, days)
    factor = num_miners / 10
    df[["BTC Mined/Day","Net Daily Revenue ($)","Cumulative BTC","Cumulative Net Revenue ($)","Final Net Revenue ($)"]] *= factor

    col0,col1,col2,col3 = st.columns(4)
    col0.metric("Project Duration", f"{years} yrs")
    col1.metric("Total BTC Mined", f"{df['Cumulative BTC'].iloc[-1]:.4f} BTC")
    col2.metric("Final Net Revenue", f"${df['Final Net Revenue ($)'].iloc[-1]:,.2f}")
    brek = df[df['Final Net Revenue ($)']>0]
    col3.metric("Breakeven", brek.iloc[0]["Date"].strftime("%Y-%m-%d") if not brek.empty else "Not Achieved")

    if view_mode=="Monthly":
        monthly = df.groupby("Month").agg({
            "Net Daily Revenue ($)":"sum",
            "BTC Mined/Day":"sum",
            "BTC Price ($)":"mean"
        }).rename(columns={
            "Net Daily Revenue ($)":"Monthly Revenue ($)",
            "BTC Mined/Day":"Monthly BTC Mined",
            "BTC Price ($)":"Avg BTC Price ($)"
        })
        st.subheader("📊 Monthly Revenue")
        st.line_chart(monthly[["Monthly Revenue ($)"]])
        st.subheader("📊 Monthly BTC Mined")
        st.line_chart(monthly[["Monthly BTC Mined"]])
        st.subheader("📋 Monthly Projection Table")
        st.dataframe(monthly)

    else:
        st.subheader("📊 Daily Net Revenue")
        st.line_chart(df.set_index("Date")[["Net Daily Revenue ($)"]])
        st.subheader("📊 Daily BTC Mined")
        st.line_chart(df.set_index("Date")[["BTC Mined/Day"]])
        st.subheader("📋 Daily Projection Table")
        st.dataframe(df[["Date","BTC Mined/Day","BTC Price ($)","Net Daily Revenue ($)"]])

with tab2:
    st.markdown("Miner comparison not implemented in this dynamic view.")

with tab3:
    st.markdown("""### Setup Cost

- Power Line: $6500  
- Rack: $600  
- PDUs: $400  
- Ventilation: $750  
- Soundproofing: $450  

**Total: $8700**""")
