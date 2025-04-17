
import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="Used Bitcoin Mining ROI Dashboard", layout="wide")
st.title("📊 Used Bitcoin Mining ROI Dashboard")

projection_file = "Bitcoin_Mining_Projection_DashboardUI.xlsx"
comparison_file = "Bitcoin_Mining_Comparison_WithHardwareCost.xlsx"

tab1, tab2, tab3 = st.tabs(["S19j Pro (Used) ROI", "Compare Used Miners", "Setup Cost Details"])

with tab1:
    df = pd.read_excel(projection_file, sheet_name="Sheet1", engine="openpyxl")
    monthly_df = pd.read_excel(projection_file, sheet_name="Monthly Summary", engine="openpyxl")

    st.subheader("🔑 Key Metrics")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total BTC Mined", f"{df['Cumulative BTC'].iloc[-1]:.4f} BTC")
    col2.metric("Final Net Revenue", f"${df['Final Net Revenue ($)'].iloc[-1]:,.2f}")
    breakeven_row = df[df['Final Net Revenue ($)'] > 0].iloc[0]
    col3.metric("ROI Breakeven Date", breakeven_row['Date'].strftime("%Y-%m-%d"))

    st.subheader("📈 Monthly Revenue")
    st.altair_chart(alt.Chart(monthly_df).mark_line(point=True).encode(
        x='Month:T',
        y='Monthly Revenue ($):Q'
    ).properties(width=800, height=300), use_container_width=True)

    st.subheader("🪙 Monthly BTC Mined")
    st.altair_chart(alt.Chart(monthly_df).mark_line(point=True, color="orange").encode(
        x='Month:T',
        y='Monthly BTC Mined:Q'
    ).properties(width=800, height=300), use_container_width=True)

    st.subheader("📋 Monthly Revenue & BTC Mined Table")
    monthly_df["Cumulative Revenue ($)"] = monthly_df["Monthly Revenue ($)"].cumsum()
    monthly_df["Cumulative BTC Mined"] = monthly_df["Monthly BTC Mined"].cumsum()
    table_df = monthly_df[["Month", "Monthly Revenue ($)", "Monthly BTC Mined", "Cumulative Revenue ($)", "Cumulative BTC Mined"]]
    st.download_button("⬇️ Download Monthly Data (CSV)", data=table_df.to_csv(index=False), file_name="s19j_monthly_data.csv", mime="text/csv")
    st.dataframe(table_df.style.format({
        "Monthly Revenue ($)": "${:,.2f}",
        "Monthly BTC Mined": "{:,.6f}",
        "Cumulative Revenue ($)": "${:,.2f}",
        "Cumulative BTC Mined": "{:,.6f}"
    }), use_container_width=True)
