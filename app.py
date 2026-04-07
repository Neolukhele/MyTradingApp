import streamlit as st
import yfinance as yf
import pandas_ta as ta
import requests
import pandas as pd
import plotly.graph_objects as go

# 1. FIX: Setup the Page
st.set_page_config(page_title="Hybrid Alpha Pro", layout="wide")

# 2. FIX: Data Cleaner for 2026
def get_clean_data(ticker):
    df = yf.download(ticker, period="1mo", interval="1h")
    if not df.empty:
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df
    return None

# 3. Simple Dashboard UI
st.title("📈 My Hybrid Trading Dashboard")
symbol = st.sidebar.text_input("Enter Ticker (e.g. BTC-USD or GBPUSD=X)", "GBPUSD=X")

data = get_clean_data(symbol)

if data is not None:
    # Indicators
    data['EMA_200'] = ta.ema(data['Close'], length=200)
    
    # Simple Signal
    last_price = data['Close'].iloc[-1]
    last_ema = data['EMA_200'].iloc[-1]
    
    col1, col2 = st.columns(2)
    col1.metric("Current Price", f"{last_price:.4f}")
    status = "BULLISH" if last_price > last_ema else "BEARISH"
    col2.subheader(f"Market Status: {status}")

    # Chart
    fig = go.Figure(data=[go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'])])
    fig.add_trace(go.Scatter(x=data.index, y=data['EMA_200'], line=dict(color='yellow')))
    fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.error("Waiting for data... check your ticker symbol!")
