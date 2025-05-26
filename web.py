import streamlit as st
import yfinance as yf

import pandas as pd
import numpy as np

from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt

import plotly.graph_objects as go

# ======== Web Config ========
st.set_page_config(page_title="📈 Stock Dashboard", layout="wide")
st.title("📊 Stock Market Dashboard")
# ============================
# ============  Sidebar ==========
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

chart = st.sidebar.selectbox(
"Chart type",
options=list(["Candle stick","Line Chart"]),
index=1
)
# ============ End Sidebar ========
# ============== Code ================
if ticker.strip() != "":
    #Download Dataframe from yfinance
    data = yf.Ticker(ticker).history(period=periods_dict[periods])
    df = data.reset_index()
    info = yf.Ticker(ticker).info



    #Check Error (When Data is empty)
    if not data.empty:
        st.success("✅ Successful")
        # ============== Basic Info ===============
        st.markdown(f"**Company Name :** {info['longName']}")
        st.markdown(f"**Sector :** {info['sector']}")

        st.markdown(f"**Market Cap :** {info['marketCap']:,.2f} {info['currency']}")
        st.markdown(f"**Shares Outstanding :** {info['sharesOutstanding']:,.0f}")

        # ========= Feature 3 : Can be displayed as a graph. There is a hypothetical price line that is trending the price. Therefore, every time you update a data, the graph will change continuously. ======        
        if chart == "Line Chart" :
            col1,col2 ,col3 = st.columns(3)

            # ===== Column 1 =================
            with col1:
                if periods != "1 day":  
                    df_sorted = df.sort_values("Date")
                    X = df_sorted["Date"].map(pd.Timestamp.toordinal).values.reshape(-1, 1)
                    y = df_sorted["Close"].values
                    model = LinearRegression()
                    model.fit(X, y)
                    trend = model.predict(X)

                    fig = plt.figure(figsize=(12, 8))
                    plt.plot(df_sorted["Date"], y, label="Actual Closing Price")
                    plt.plot(df_sorted["Date"], trend, label="Trend (Linear Regression)",
                                linestyle="--", color="red")
                    plt.title("KTC Closing Price Trend")
                    plt.xlabel("Date")
                    plt.ylabel("Closing Price (Baht)")
                    plt.legend()
                    plt.grid(True)
                    plt.tight_layout()

                    #plot line chart
                    st.pyplot(fig)

            # ===== End Column 1 ==============
            # ===== Column 2 ==================
            with col2:
                if periods in ("1 month", "3 months", "6 months" , "1 year"):
                    # Sum Volume
                    monthly_volume = data["Volume"].resample("M").sum()

                    fig, ax = plt.subplots(figsize=(10, 6))
                    ax.bar(monthly_volume.index.strftime("%b %Y"), monthly_volume.values, color='red')
                    ax.set_title("Volume Monthly KTC")
                    ax.set_ylabel("Volume (Millions)")
                    ax.set_xlabel("Month")
                    plt.xticks(rotation=45)
                    #plot bar chart
                    st.pyplot(fig)
            # ===== End Column 2 ==============
            # ===== Column 3 ==================      
            with col3 :
                if periods != "1 day": 
                    # Cal EMA 12 and EMA 26
                    ema12 = df['Close'].ewm(span=12, adjust=False).mean()
                    ema26 = df['Close'].ewm(span=26, adjust=False).mean()

                    # Cal MACD line
                    df['MACD'] = ema12 - ema26

                    # คำนวณ Signal line (EMA 9 ของ MACD)
                    df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()

                    # plot MACD และ Signal line
                    fig, ax = plt.subplots(figsize=(12, 8))
                    ax.plot(df.index, df['MACD'], label='MACD', color='blue')
                    ax.plot(df.index, df['Signal'], label='Signal', color='red')
                    ax.set_title('MACD vs Signal Line')
                    ax.legend()
                    ax.grid(True)

                    st.pyplot(fig)
            # ===== End Column 3 ==============
        else : 
            col1 = st.columns(1)
            # Cal MACD
            ema12 = df['Close'].ewm(span=12, adjust=False).mean()
            ema26 = df['Close'].ewm(span=26, adjust=False).mean()
            macd = ema12 - ema26
            signal = macd.ewm(span=9, adjust=False).mean()
            hist = macd - signal

            # Plotly Graph
            fig = go.Figure()

            # CandleStick
            fig.add_trace(go.Candlestick(
                            x=df.index,
                            open=df['Open'],
                            high=df['High'],
                            low=df['Low'],
                            close=df['Close'],
                            name='Candlestick',
                            increasing_line_color='green',
                            decreasing_line_color='red',
                            yaxis='y1'
                        ))

            # MACD line
            fig.add_trace(go.Scatter(
                            x=df.index, y=macd,
                            line=dict(color='blue'),
                            name='MACD',
                            yaxis='y2'
                        ))

            # Signal line
            fig.add_trace(go.Scatter(
                            x=df.index, y=signal,
                            line=dict(color='orange'),
                            name='Signal',
                            yaxis='y2'
                        ))

            # Histogram
            fig.add_trace(go.Bar(
                            x=df.index, y=hist,
                            name='Histogram',
                            marker_color='gray',
                            opacity=0.3,
                            yaxis='y2'
                        ))

            # Edit layout
            fig.update_layout(
                            xaxis=dict(domain=[0, 1]),
                            yaxis=dict(title='Price'),
                            yaxis2=dict(
                                title='MACD',
                                overlaying='y',
                                side='right',
                                showgrid=False
                            ),
                            height=600,
                            xaxis_rangeslider_visible=False,
                            legend=dict(x=0, y=1.2, orientation='h')
                        )

            st.plotly_chart(fig, use_container_width=True)
        # ========== End Feature 3 ========================
        # ====== Feature 2 : Visualize data such as top 5, mean, median etc . ======
        #========== CSS =================
        st.markdown(
            """
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
            """
        , unsafe_allow_html=True)
        # ========= End CSS =============
        #Create column (Last Update Date , Average Open , Average Close , Last Volume , Most Volume)
        col1, col2, col3, col4 = st.columns(4)
        # ===== Column 1 ================== 
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
        # ===== End Column 1 ==============
        # ===== Column 2 ================== 
        with col2:
            EMA20 = df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean().iloc[-1]
            st.markdown(f"""<div class="card">
                                <div class="value">
                                    {EMA20:,.2f}
                                </div>
                            <div class="label">
                                EMA 20
                            </div>
                            </div>"""
                        , unsafe_allow_html=True)
        # ===== End Column 2 ==============             
        # ===== Column 3 ==================
        with col3:
            delta = df['Close'].diff()
            gain = delta.clip(lower=0)
            loss = -delta.clip(upper=0)

            avg_gain = gain.rolling(window=14).mean().iloc[-1]
            avg_loss = loss.rolling(window=14).mean().iloc[-1]

            rs = avg_gain / avg_loss
            RSI14 = 100 - (100 / (1 + rs))
            if RSI14 < 30 : rsi_result = "Oversold"
            elif RSI14 > 70 : rsi_result = "Overbought"
            elif RSI14 > 30 and RSI14 < 70  : rsi_result = "Normal"
            else : rsi_result = "Please select more data"; RSI14 = 0
            st.markdown(f"""<div class="card">
                                <div class="value">
                                    {RSI14:,.2f} ({rsi_result}) 
                                </div>
                            <div class="label">
                                RSI 14
                            </div>
                            </div>"""
                        , unsafe_allow_html=True)
        # ===== End Column 3 ==============
        # ===== Column 4 ================== 
        with col4:
            ma20 = df['Close'].rolling(window=20).mean()
            std20 = df['Close'].rolling(window=20).std()
            upper = ma20 + 2 * std20
            lower = ma20 - 2 * std20

            
            df['%B'] = (df['Close'] - lower) / (upper - lower)
            last_percent_b = df['%B'].iloc[-1]

            st.markdown(f"""<div class="card">
                                <div class="value">
                                    {last_percent_b:.2%}
                                </div>
                            <div class="label">
                                % Bollinger
                            </div>
                            </div>"""
                        , unsafe_allow_html=True)
        # ===== End Column 4 ==============
        # ====== End Feature 2 ============================ 
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
    # ====== End  Feature 1 ==================================
#Instruction Error
else:
    st.info("Please Input the Stock First")
# ============ End Code====================================