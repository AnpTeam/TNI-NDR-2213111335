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

# ====== Code ======
if ticker.strip() != "":
    #Download Dataframe from yfinance
    data = yf.Ticker(ticker).history(period=periods_dict[periods])
    df = data.reset_index()

    #Check Error (When Data is empty)
    if not data.empty:
        st.success("✅ Successful")

        # ====== Feature 2 : Visualize data such as top 5, mean, median etc . ======
        st.markdown("""
        <style>
        .card {
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }
        .value {
            font-size: 24px;
            font-weight: lighter;
        }
        .label {
            font-size: 18px;
            color: rgb(255, 75, 75);
            font-weight: bold;
        }
        </style>
        """, unsafe_allow_html=True)

        #Create column (Last Update Date , Average Open , Average Close , Last Volume , Most Volume)
        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.markdown(f"""<div class="card">
                                <div class="value">
                                    {df["Date"].max().strftime("%d-%b-%Y")}
                                </div>
                            <div class="label">
                                Last Update Date
                            </div>
                            </div>"""
                        , unsafe_allow_html=True)

        with col2:
            st.markdown(f"""<div class="card">
                                <div class="value">
                                    {df["Open"].mean():,.2f}
                                </div>
                            <div class="label">
                                Average Open Price
                            </div>
                            </div>"""
                        , unsafe_allow_html=True)

        with col3:
            st.markdown(f"""<div class="card">
                                <div class="value">
                                    {df["Close"].mean():,.2f}
                                </div>
                            <div class="label">
                                Average Close Price
                            </div>
                            </div>"""
                        , unsafe_allow_html=True)

        with col4:
            st.markdown(f"""<div class="card">
                                <div class="value">
                                    {df["Volume"].iloc[-1]:,.2f}
                                </div>
                            <div class="label">
                                Last Volume
                            </div>
                            </div>"""
                        , unsafe_allow_html=True)

        with col5:
            st.markdown(f"""<div class="card">
                                <div class="value">
                                    {df["Volume"].max():,.2f}
                                </div>
                            <div class="label">
                                Max Volume
                            </div>
                            </div>"""
                        , unsafe_allow_html=True)
        # ===========================

        # ====== Feature 1 : Can view recent prices in different time and download them in CSV format. ======
        #Select Some column
        columns = st.multiselect("Select Column to Display", df.columns.tolist(), default=["Date", "Open", "High", "Low", "Close", "Volume"])
        select_df = df[columns]
        
        #Style each Column
        styled_df = select_df.style.format({
            "Date": lambda t: t.strftime("%d-%b-%Y"),
            "Open": "{:.2f}",
            "High": "{:.3f}",
            "Low": "{:.2f}",
            "Close": "{:.2f}",
            "Volume": "{:,.0f}",
            "Dividends":"{:.2f}",
            "Stock Splits":"{:.2f}",
        })

        st.dataframe(styled_df)

        # Get the CSV file
        csv = data.to_csv().encode("utf-8")

        # Download Button
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"{ticker}_{periods}.csv",
            mime="text/csv"
            )
    else:
        st.error("❌ This Stock Not Found")
else:
    st.info("Please Input the Stock First")
# ===========================
# ============ End Code===============



