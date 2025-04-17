
import streamlit as st
import pandas as pd
import altair as alt
import os

st.set_page_config(page_title="Used Bitcoin Mining ROI Dashboard", layout="wide")
st.title("📊 Used Bitcoin Mining ROI Dashboard")

projection_file = "Bitcoin_Mining_Projection_DashboardUI.xlsx"
comparison_file = "Bitcoin_Mining_Comparison_WithHardwareCost.xlsx"

tab1, tab2, tab3 = st.tabs(["S19j Pro (Used) ROI", "Compare Used Miners", "Setup Cost Details"])

with tab1:
    if os.path.exists(projection_file):
        try:
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

        except Exception as e:
            st.error(f"❌ Error loading Excel sheets from {projection_file}: {e}")
    else:
        st.warning(f"📁 File not found: {projection_file}. Please ensure it's in the same directory.")

with tab2:
    if os.path.exists(comparison_file):
        try:
            st.header("📊 Antminer Comparison")
            models = ["S19j Pro", "S19 XP", "S21 Hydro"]
            for model in models:
                st.subheader(f"📈 {model} ROI")
                df_model = pd.read_excel(comparison_file, sheet_name=model, engine="openpyxl")

                col1, col2, col3 = st.columns(3)
                col1.metric("Total BTC Mined", f"{df_model['Cumulative BTC'].iloc[-1]:.4f} BTC")
                col2.metric("Final Net Revenue", f"${df_model['Final Net Revenue ($)'].iloc[-1]:,.2f}")
                col3.metric("Hardware Cost (10 units)", f"${int(df_model['Hardware Cost ($)'].iloc[0]):,}")
                breakeven_row = df_model[df_model['Cumulative Revenue ($)'] > df_model['Hardware Cost ($)'].iloc[0]].iloc[0]
                st.metric("ROI Breakeven Date", breakeven_row['Date'].strftime("%Y-%m-%d"))

                st.subheader("📊 Cumulative Revenue Over Time")
                df_model["Cumulative Revenue ($)"] = df_model["Net Daily Revenue ($)"].cumsum()
                st.line_chart(df_model[["Date", "Cumulative Revenue ($)"]].set_index("Date"))

                st.subheader("📋 Monthly Summary Table")
                df_model["Month"] = df_model["Date"].dt.to_period("M").dt.to_timestamp()
                monthly_group = df_model.groupby("Month").agg({
                    "Net Daily Revenue ($)": "sum",
                    "BTC Mined/Day": "sum"
                }).rename(columns={
                    "Net Daily Revenue ($)": "Monthly Revenue ($)",
                    "BTC Mined/Day": "Monthly BTC Mined"
                }).reset_index()
                monthly_group["Cumulative BTC Mined"] = monthly_group["Monthly BTC Mined"].cumsum()
                monthly_group["Cumulative Revenue ($)"] = monthly_group["Monthly Revenue ($)"].cumsum()
                st.download_button("⬇️ Download Monthly Comparison Data (CSV)", data=monthly_group.to_csv(index=False), file_name=f"{model.lower()}_monthly_data.csv", mime="text/csv")
                st.dataframe(monthly_group.style.format({
                    "Monthly Revenue ($)": "${:,.2f}",
                    "Monthly BTC Mined": "{:,.6f}",
                    "Cumulative Revenue ($)": "${:,.2f}",
                    "Cumulative BTC Mined": "{:,.6f}"
                }), use_container_width=True)

            st.subheader("📊 ROI Comparison Summary")
            st.image("roi_chart.png")

            st.subheader("⏱️ Payback Time to Recover Hardware Cost")
            st.image("payback_chart.png")

        except Exception as e:
            st.error(f"❌ Error loading Excel sheets from {comparison_file}: {e}")
    else:
        st.warning(f"📁 File not found: {comparison_file}. Please ensure it's in the same directory.")

with tab3:
    st.markdown("""
### 💡 Setup Cost Breakdown

| Component                     | Description                                                                 | Estimated Cost |
|------------------------------|-----------------------------------------------------------------------------|----------------|
| ⚡ **Power Installation**     | 100 ft trench, 240V line, conduit, wire, breakers, subpanel, electrician   | **$3,245**     |
| 🗄️ **Mining Rack**            | Heavy-duty vertical rack for 10 Antminers                                  | **$600**       |
| 🔌 **PDUs**                   | Industrial-grade Power Distribution Units (e.g., L6-30P, C13/C19 outlets)   | **$400**       |
| 🌬️ **Ventilation System**     | High-CFM intake/exhaust fans, ducting, filters                              | **$750**       |
| 🔇 **Soundproofing Materials**| Mineral wool, foam insulation, door seals                                  | **$450**       |

**Total Setup Cost: $5,445**
    """)
