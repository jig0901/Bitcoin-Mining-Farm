
import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="Bitcoin Mining ROI Dashboard", layout="wide")

st.title("📊 Bitcoin Mining ROI Dashboard")

uploaded_file = st.file_uploader("Upload ROI Excel File", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file, sheet_name="Sheet1", engine="openpyxl")
    monthly_df = pd.read_excel(uploaded_file, sheet_name="Monthly Summary", engine="openpyxl")

    # KPI Summary
    st.subheader("🔑 Key Metrics")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total BTC Mined", f"{df['Cumulative BTC'].iloc[-1]:.4f} BTC")
    col2.metric("Final Net Revenue", f"${df['Final Net Revenue ($)'].iloc[-1]:,.2f}")
    breakeven_row = df[df['Final Net Revenue ($)'] > 0].iloc[0]
    col3.metric("ROI Breakeven Date", breakeven_row['Date'].strftime("%Y-%m-%d"))

    # Charts
    st.subheader("📈 Monthly Revenue")
    chart_rev = alt.Chart(monthly_df).mark_line(point=True).encode(
        x='Month:T',
        y='Monthly Revenue ($):Q'
    ).properties(width=800, height=300)
    st.altair_chart(chart_rev, use_container_width=True)

    st.subheader("🪙 Monthly BTC Mined")
    chart_btc = alt.Chart(monthly_df).mark_line(point=True, color="orange").encode(
        x='Month:T',
        y='Monthly BTC Mined:Q'
    ).properties(width=800, height=300)
    st.altair_chart(chart_btc, use_container_width=True)

    # Raw Data Preview
    with st.expander("🔍 View Raw Data"):
        st.dataframe(monthly_df)
else:
    st.info("Please upload the Excel file with projection data (Sheet1 and Monthly Summary required).")
