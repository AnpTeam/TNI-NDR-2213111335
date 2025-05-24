import streamlit as st
import yfinance as yf

import pandas as pd
import numpy as np

from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt

# ======== Web Config =======
st.set_page_config(page_title="📈 Stock Dashboard", layout="wide")
st.title("📊 Stock Market Dashboard")
# ===========================

# ========  Sidebar =========
periods_dict = {
    "1 day": "1d",
    "7 days": "7d",
    "1 month": "1mo",
    "3 months" : "3mo",
    "6 months" : "6mo",
    "1 year" : "1y"
}

st.sidebar.header("🔍 Stock Options")
ticker = st.sidebar.text_input("Enter Stock Symbol", value="KTC.BK")
periods = st.sidebar.selectbox(
    "Period",
    options=list(periods_dict.keys()),
    index=4
)
# ===========================

# ====== Feature 1 : Can view recent prices in 6 month and download them in CSV format. ======
if ticker.strip() != "":
    #Download Dataframe from yfinance
    data = yf.Ticker(ticker).history(period=periods_dict[periods])
    df = data.reset_index()

    #Check Error (When Data is empty)
    if not data.empty:
        st.success("✅ Successful")

        styled_df = df.style.format({
            "Date": lambda t: t.strftime("%d-%b-%Y %H:%M"),
            "Open": "{:.2f}",
            "High": "{:.3f}",
            "Low": "{:.2f}",
            "Close": "{:.2f}",
            "Volume": "{:,.0f}"
        })
        st.dataframe(styled_df)

        # Get the CSV file
        csv = data.to_csv().encode("utf-8")

        # Download Button
        st.download_button(
            label="📥 ดาวน์โหลด CSV",
            data=csv,
            file_name=f"{ticker}_{periods}.csv",
            mime="text/csv"
            )
    else:
        st.error("❌ This Stock Not Found")
else:
    st.info("Please Input the Stock First")
# ===========================


