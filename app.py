import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Hybrid Trader 2026", layout="wide")

st.title("📈 Hybrid Intelligence Dashboard")

# The "Simple" Ticker Input
symbol = st.sidebar.text_input("Ticker (e.g. BTC-USD)", "GBPUSD=X")

# Fetch Data
df = yf.download(symbol, period="1mo", interval="1h")

if not df.empty:
    # Manual EMA Calculation (No Numba/TA required!)
    df['EMA_200'] = df['Close'].ewm(span=200, adjust=False).mean()
    
    # Logic
    last_price = df['Close'].iloc[-1]
    last_ema = df['EMA_200'].iloc[-1]
    
    c1, c2 = st.columns(2)
    c1.metric("Live Price", f"{last_price:.4f}")
    c2.metric("Trend Status", "BULLISH" if last_price > last_ema else "BEARISH")

    # Charting
    fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
    fig.add_trace(go.Scatter(x=df.index, y=df['EMA_200'], line=dict(color='yellow'), name="Trend Line"))
    fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.error("Check your Ticker symbol!")
