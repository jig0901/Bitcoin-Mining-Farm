
# 🧮 Bitcoin Mining ROI Dashboard

This Streamlit-powered dashboard provides a real-time visualization and summary of your Bitcoin mining operation. Upload your mining ROI Excel file to get live KPIs, revenue charts, and breakeven metrics.

---

## 📁 Included Files

- `bitcoin_mining_dashboard.py` – Main dashboard script
- `Bitcoin_Mining_Projection_DashboardUI.xlsx` – Example ROI data file with projections and monthly summary

---

## 🚀 Running Locally

```bash
pip install streamlit pandas openpyxl altair
streamlit run bitcoin_mining_dashboard.py
```

---

## ☁️ Deploy on Streamlit Cloud

1. Fork this repo or upload the files to your GitHub
2. Go to [Streamlit Cloud](https://streamlit.io/cloud) and link your repo
3. Deploy and customize!

---

## 📊 Features

- 📈 Monthly BTC Mined and Revenue Charts
- 🔑 Total BTC Mined, Net Profit, Breakeven Date
- 🔄 Upload new Excel files dynamically
- 💸 Built for ASIC mining projections (S19j Pro, S19 XP, etc.)

---

## 📎 Excel Template Format

Required sheets:
- `Sheet1` (Projections with date-wise ROI data)
- `Monthly Summary` (Aggregated monthly BTC and revenue)

You can generate these from our modeling tool or use your own format.
