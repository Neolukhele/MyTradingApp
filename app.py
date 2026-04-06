import streamlit as st
import yfinance as yf
import pandas_ta as ta
import requests
import pandas as pd
import plotly.graph_objects as go

# --- 1. SYSTEM SECURITY ---
ALPHA_KEY = "YOUR_FREE_KEY" # Get at alphavantage.co

st.set_page_config(page_title="HYBRID ALPHA PRO", layout="wide", page_icon="🏦")

# --- 2. DATA ENGINE (AUDITED & FLATTENED) ---
def get_verified_data(symbol, interval):
    try:
        df = yf.download(symbol, period="1mo", interval=interval)
        if df.empty: return None
        
        # Pass 1 Fix: Force column flattening for 2026 yfinance structure
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        df['EMA_200'] = ta.ema(df['Close'], length=200)
        df['RSI'] = ta.rsi(df['Close'], length=14)
        return df
    except Exception as e:
        st.error(f"Data Error: {e}")
        return None

# --- 3. NEWS ENGINE (AUDITED & CACHED) ---
def get_daily_news(asset):
    # Pass 2 Fix: Prevent API burnout using manual refresh logic
    if 'news_cache' not in st.session_state:
        url = f'https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={asset}&apikey={ALPHA_KEY}'
        r = requests.get(url)
        data = r.json()
        st.session_state.news_cache = data.get("feed", [])[:3]
    return st.session_state.news_cache

# --- 4. THE INSTITUTIONAL DASHBOARD ---
st.title("🏛️ Institutional Hybrid Dashboard")

col_main, col_news = st.columns([3, 1])

with col_main:
    pair = st.text_input("Asset Ticker (e.g., GBPUSD=X, TSLA, GC=F)", "GBPUSD=X")
    data = get_verified_data(pair, "1h")
    
    if data is not None:
        fig = go.Figure(data=[go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], name="Market")])
        fig.add_trace(go.Scatter(x=data.index, y=data['EMA_200'], line=dict(color='yellow', width=1.5), name="200 EMA (Trend)"))
        fig.update_layout(template="plotly_dark", height=600, xaxis_rangeslider_visible=False, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

with col_news:
    st.subheader("🌍 Daily World Context")
    if st.button("🔄 Refresh World News"):
        if 'news_cache' in st.session_state: del st.session_state.news_cache
        st.rerun()
        
    news = get_daily_news(pair.split('=')[0]) # Strip '=X' for news search
    for item in news:
        st.markdown(f"**{item['title']}**")
        st.caption(f"Sentiment: {item['overall_sentiment_label']}")
        st.write(f"{item['summary'][:150]}...")
        st.divider()

# --- 5. THE DECISION MATRIX ---
if data is not None:
    st.sidebar.header("🤖 AI Decision")
    last_price = data['Close'].iloc[-1]
    last_ema = data['EMA_200'].iloc[-1]
    
    # Simple Rule: Price > EMA = Bullish | Price < EMA = Bearish
    market_state = "BULLISH" if last_price > last_ema else "BEARISH"
    color = "green" if market_state == "BULLISH" else "red"
    
    st.sidebar.markdown(f"### Current State: :{color}[{market_state}]")
    st.sidebar.write("Ensure your News sentiment in the right panel matches this chart direction before entering.")
