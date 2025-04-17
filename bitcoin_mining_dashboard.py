# placeholder for bitcoin_mining_dashboard.py

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
