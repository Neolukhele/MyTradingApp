import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Hybrid Trader 2026", layout="wide")

st.title("📈 Hybrid Intelligence Dashboard")

# 1. Input for the Asset
symbol = st.sidebar.text_input("Ticker (e.g. BTC-USD or GBPUSD=X)", "GBPUSD=X")

# 2. Fetch Data
df = yf.download(symbol, period="1mo", interval="1h")

if not df.empty:
    # 3. Handle 2026 Multi-Index headers
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    # 4. Manual EMA Calculation
    df['EMA_200'] = df['Close'].ewm(span=200, adjust=False).mean()
    
    # --- THE FIX IS HERE ---
    # We use .iloc[-1] and then .item() to ensure we have a single decimal number
    last_price = float(df['Close'].iloc[-1])
    last_ema = float(df['EMA_200'].iloc[-1])
    
    c1, c2 = st.columns(2)
    c1.metric("Live Price", f"{last_price:.4f}")
    
    status = "BULLISH" if last_price > last_ema else "BEARISH"
    color = "normal" if status == "BULLISH" else "inverse"
    c2.metric("Trend Status", status, delta_color=color)

    # 5. The Chart
    fig = go.Figure(data=[go.Candlestick(
        x=df.index, 
        open=df['Open'], 
        high=df['High'], 
        low=df['Low'], 
        close=df['Close'],
        name="Price"
    )])
    
    fig.add_trace(go.Scatter(x=df.index, y=df['EMA_200'], line=dict(color='yellow'), name="200 EMA"))
    fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.error("Waiting for valid Ticker... Try 'BTC-USD'")
