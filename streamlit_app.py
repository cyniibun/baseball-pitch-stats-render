import pandas as pd
import streamlit as st
import numpy as np
import io
import openpyxl
from openpyxl.styles import PatternFill, Font
from openpyxl.utils.dataframe import dataframe_to_rows
from io import StringIO

st.set_page_config(page_title="Pitcher vs Batter Analyzer", layout="wide")
st.title("⚾ Pitcher vs Batter Matchup Analyzer")

st.markdown("""
Upload **CSV files** or paste **CSV-formatted text** for both the **pitcher** and **batter** stats below. The app will generate a color-coded matchup table:

- 🔴 Negative delta = Pitcher Advantage
- 🟢 Positive delta = Batter Advantage
""")

# Upload inputs
pitcher_file = st.file_uploader("📤 Upload Pitcher CSV", type="csv")
batter_file = st.file_uploader("📤 Upload Batter CSV", type="csv")

# Text paste alternative
st.subheader("📝 Paste Pitcher CSV Data (optional)")
pitcher_text = st.text_area("Paste CSV-formatted text for pitcher stats")

st.subheader("📝 Paste Batter CSV Data (optional)")
batter_text = st.text_area("Paste CSV-formatted text for batter stats")

# Attempt to load data from files or text
pitcher_df = None
batter_df = None

try:
    if pitcher_file:
        pitcher_df = pd.read_csv(pitcher_file)
    elif pitcher_text:
        pitcher_df = pd.read_csv(StringIO(pitcher_text))
except Exception as e:
    st.error(f"❌ Error reading pitcher data: {e}")

try:
    if batter_file:
        batter_df = pd.read_csv(batter_file)
    elif batter_text:
        batter_df = pd.read_csv(StringIO(batter_text))
except Exception as e:
    st.error(f"❌ Error reading batter data: {e}")

# Proceed if both datasets are available
if pitcher_df is not None and batter_df is not None:
    try:
        # Merge and compute deltas
        merged = pd.merge(pitcher_df, batter_df, on="Pitch", suffixes=("_Pitcher", "_Batter"))

        for stat in ["K%", "Whiff%", "PutAway%", "OBA", "BA", "SLG"]:
            merged[f"{stat} Delta"] = merged[f"{stat}_Pitcher"] - merged[f"{stat}_Batter"]

        # Delta column styling
        def color_deltas(val):
            if pd.isnull(val): return ""
            if val <= -45: return "background-color:#990000; color:white"
            elif val <= -20: return "background-color:#e06666"
            elif val < 0: return "background-color:#f4cccc"
            elif val <= 20: return "background-color:#d9ead3"
            elif val <= 45: return "background-color:#93c47d"
            else: return "background-color:#38761d; color:white"

        delta_cols = [col for col in merged.columns if "Delta" in col]
        styled = merged.style.applymap(color_deltas, subset=delta_cols)

        st.subheader("📊 Matchup Analysis Table")
        st.dataframe(styled, use_container_width=True)

        # Download CSV
        st.download_button(
            label="📥 Download as CSV",
            data=merged.to_csv(index=False).encode("utf-8"),
            file_name="matchup_analysis.csv",
            mime="text/csv"
        )

        # Download Excel
        output = io.BytesIO()
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Matchup"

        for r in dataframe_to_rows(merged, index=False, header=True):
            ws.append(r)

        for cell in ws[1]:
            cell.font = Font(bold=True)
            cell.fill = PatternFill(start_color="DDDDDD", end_color="DDDDDD", fill_type="solid")

        wb.save(output)
        st.download_button(
            label="📊 Download as Excel (.xlsx)",
            data=output.getvalue(),
            file_name="matchup_analysis.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        st.error(f"❌ Error processing data: {e}")
else:
    st.info("📂 Please upload or paste both pitcher and batter data to begin analysis.")