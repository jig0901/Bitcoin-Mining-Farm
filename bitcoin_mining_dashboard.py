import streamlit as st
import pandas as pd
import altair as alt

# ─── Page setup ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Used Bitcoin Mining Farm ROI Dashboard",
    layout="wide"
)
st.title("📊 Used Bitcoin Mining Farm ROI Dashboard")

# ─── Data files ────────────────────────────────────────────────────────────────
projection_file = "Bitcoin_Mining_Projection_DashboardUI.xlsx"
comparison_file = "Bitcoin_Mining_Comparison_WithHardwareCost.xlsx"

# ─── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs([
    "S19j Pro ROI",
    "Compare Miners",
    "Setup Cost Details"
])

# ─── Tab1: S19j Pro detailed projection ────────────────────────────────────────
with tab1:
    df = pd.read_excel(projection_file, sheet_name="Sheet1", engine="openpyxl")
    monthly_df = pd.read_excel(projection_file, sheet_name="Monthly Summary", engine="openpyxl")

    st.subheader("🔑 Key Metrics")
    c1, c2, c3 = st.columns(3)
    c1.metric("Total BTC Mined", f"{df['Cumulative BTC'].iloc[-1]:.4f} BTC")
    c2.metric("Final Net Revenue", f"${df['Final Net Revenue ($)'].iloc[-1]:,.2f}")
    breakeven = df[df['Final Net Revenue ($)'] > 0].iloc[0]
    c3.metric("ROI Breakeven Date", breakeven['Date'].strftime("%Y-%m-%d"))

    st.subheader("📈 Monthly Revenue")
    st.altair_chart(
        alt.Chart(monthly_df).mark_line(point=True).encode(
            x='Month:T',
            y='Monthly Revenue ($):Q'
        ).properties(width=800, height=300),
        use_container_width=True
    )

    st.subheader("🪙 Monthly BTC Mined")
    st.altair_chart(
        alt.Chart(monthly_df).mark_line(point=True, color="orange").encode(
            x='Month:T',
            y='Monthly BTC Mined:Q'
        ).properties(width=800, height=300),
        use_container_width=True
    )

    st.subheader("📋 Monthly Revenue & BTC Mined Table")
    monthly_df["Cumulative Revenue ($)"] = monthly_df["Monthly Revenue ($)"].cumsum()
    monthly_df["Cumulative BTC Mined"] = monthly_df["Monthly BTC Mined"].cumsum()
    table_df = monthly_df[[
        "Month",
        "Monthly Revenue ($)",
        "Monthly BTC Mined",
        "Cumulative Revenue ($)",
        "Cumulative BTC Mined"
    ]]
    st.download_button(
        "⬇️ Download Monthly Data (CSV)",
        data=table_df.to_csv(index=False),
        file_name="s19j_monthly_data.csv",
        mime="text/csv"
    )
    st.dataframe(
        table_df.style.format({
            "Monthly Revenue ($)": "${:,.2f}",
            "Monthly BTC Mined": "{:,.6f}",
            "Cumulative Revenue ($)": "${:,.2f}",
            "Cumulative BTC Mined": "{:,.6f}"
        }),
        use_container_width=True
    )

# ─── Tab2: Compare Miners ───────────────────────────────────────────────────────
with tab2:
    st.header("📊 Antminer Comparison")

    models = ["S19j Pro", "S19 XP", "S21 Hydro"]
    for model in models:
        st.subheader(f"📈 {model} ROI")

        if model == "S19j Pro":
            # — Use your projection sheet for S19j Pro…
            df_model = pd.read_excel(
                projection_file,
                sheet_name="Sheet1",
                engine="openpyxl"
            )
            # …but grab its hardware cost from the comparison workbook
            cost_df = pd.read_excel(
                comparison_file,
                sheet_name="S19j Pro",
                usecols=["Hardware Cost ($)"],
                engine="openpyxl"
            )
            hw_cost = int(cost_df["Hardware Cost ($)"].iloc[0])
            df_model["Hardware Cost ($)"] = hw_cost
            df_model["Model"] = "S19j Pro"
        else:
            df_model = pd.read_excel(
                comparison_file,
                sheet_name=model,
                engine="openpyxl"
            )

        # Metrics
        col1, col2, col3 = st.columns(3)
        col1.metric(
            "Total BTC Mined",
            f"{df_model['Cumulative BTC'].iloc[-1]:.4f} BTC"
        )
        col2.metric(
            "Final Net Revenue",
            f"${df_model['Final Net Revenue ($)'].iloc[-1]:,.2f}"
        )
        col3.metric(
            "Hardware Cost (10 units)",
            f"${int(df_model['Hardware Cost ($)'].iloc[0]):,}"
        )

        # Breakeven
        breakeven_row = df_model[
            df_model['Cumulative Revenue ($)'] > df_model['Hardware Cost ($)'].iloc[0]
        ].iloc[0]
        st.metric(
            "ROI Breakeven Date",
            breakeven_row['Date'].strftime("%Y-%m-%d")
        )

        # Cumulative revenue chart
        st.subheader("📊 Cumulative Revenue Over Time")
        df_model["Cumulative Revenue ($)"] = df_model["Net Daily Revenue ($)"].cumsum()
        st.line_chart(
            df_model[["Date", "Cumulative Revenue ($)"]].set_index("Date")
        )

        # Monthly summary table
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

        st.download_button(
            "⬇️ Download Monthly Comparison Data (CSV)",
            data=monthly_group.to_csv(index=False),
            file_name=f"{model.lower()}_monthly_data.csv",
            mime="text/csv"
        )
        st.dataframe(
            monthly_group.style.format({
                "Monthly Revenue ($)": "${:,.2f}",
                "Monthly BTC Mined": "{:,.6f}",
                "Cumulative Revenue ($)": "${:,.2f}",
                "Cumulative BTC Mined": "{:,.6f}"
            }),
            use_container_width=True
        )

    st.subheader("📊 ROI Comparison Summary")
    st.image("roi_chart.png")

    st.subheader("⏱️ Payback Time to Recover Hardware Cost")
    st.image("payback_chart.png")

# ─── Tab3: Setup Cost Breakdown ────────────────────────────────────────────────
with tab3:
    st.markdown("""
### 💡 Setup Cost Breakdown

| Component                     | Description                                                                 | Estimated Cost |
|-------------------------------|-----------------------------------------------------------------------------|----------------|
| ⚡ **Power Installation**     | 100 ft trench, 240V line, conduit, wire, breakers, subpanel, electrician   | **$3,245**     |
| 🗄️ **Mining Rack**            | Heavy-duty vertical rack for 10 Antminers                                  | **$600**       |
| 🔌 **PDUs**                   | Industrial-grade Power Distribution Units (e.g., L6-30P, C13/C19 outlets)   | **$400**       |
| 🌬️ **Ventilation System**     | High-CFM intake/exhaust fans, ducting, filters                              | **$750**       |
| 🔇 **Soundproofing Materials**| Mineral wool, foam insulation, door seals                                  | **$450**       |

**Total Setup Cost: $5,445**
    """)
