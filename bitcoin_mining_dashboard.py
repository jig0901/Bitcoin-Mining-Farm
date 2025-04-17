
import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="Bitcoin Mining ROI Dashboard", layout="wide")

st.title("📊 Bitcoin Mining ROI Dashboard")

tab1, tab2, tab3 = st.tabs(["S19j Pro ROI", "Compare Miners", "Setup Cost Details"])

with tab1:
    uploaded_file = st.file_uploader("Upload ROI Excel File (S19j Pro)", type=["xlsx"])
    if uploaded_file:
        df = pd.read_excel(uploaded_file, sheet_name="Sheet1", engine="openpyxl")
        monthly_df = pd.read_excel(uploaded_file, sheet_name="Monthly Summary", engine="openpyxl")

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

        with st.expander("🔍 View Raw Data"):
            st.dataframe(monthly_df)
    else:
        st.info("Please upload the Excel file for S19j Pro ROI.")

with tab2:
    st.header("📊 Antminer Comparison")
    st.markdown("Upload an Excel file with sheets named 'S19j Pro', 'S19 XP', and 'S21 Hydro'.")
    comparison_file = st.file_uploader("Upload Comparison File", type=["xlsx"], key="compare")

    if comparison_file:
        models = ["S19j Pro", "S19 XP", "S21 Hydro"]
        for model in models:
            st.subheader(f"📈 {model} ROI")
            df_model = pd.read_excel(comparison_file, sheet_name=model, engine="openpyxl")
            col1, col2, col3 = st.columns(3)
            col1.metric("Total BTC Mined", f"{df_model['Cumulative BTC'].iloc[-1]:.4f} BTC")
            col2.metric("Final Net Revenue", f"${df_model['Final Net Revenue ($)'].iloc[-1]:,.2f}")
            breakeven_row = df_model[df_model['Final Net Revenue ($)'] > 0].iloc[0]
            col3.metric("ROI Breakeven Date", breakeven_row['Date'].strftime("%Y-%m-%d"))
            st.altair_chart(alt.Chart(df_model).mark_line().encode(
                x='Date:T', y='Final Net Revenue ($):Q'
            ).properties(height=300), use_container_width=True)

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
