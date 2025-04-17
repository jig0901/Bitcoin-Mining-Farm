
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
