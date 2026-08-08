# HK-dashboard-
import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="🇭🇰 港股儀表板", layout="wide")
st.title("🇭🇰 港股與市場過熱監測")

ticker = st.selectbox("選擇監測標的", ["^HSI", "3033.HK", "2800.HK", "0700.HK"], index=0)

@st.cache_data(ttl=1800)
def load_data(symbol):
    df = yf.Ticker(symbol).history(period="1y")
    return df

try:
    df = load_data(ticker)
    
    df['SMA50'] = df['Close'].rolling(50).mean()
    df['SMA200'] = df['Close'].rolling(200).mean()
    
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))

    latest_close = df['Close'].iloc[-1]
    latest_rsi = df['RSI'].iloc[-1]
    dist_sma200 = ((latest_close - df['SMA200'].iloc[-1]) / df['SMA200'].iloc[-1]) * 100

    col1, col2 = st.columns(2)
    col1.metric("最新價", f"{latest_close:,.2f}")
    col2.metric("14日 RSI", f"{latest_rsi:.1f}")

    if latest_rsi > 70 or dist_sma200 > 15:
        st.error("⚠️ 市場處於偏熱/過熱狀態！")
    elif latest_rsi < 30:
        st.success("🧊 市場處於超賣/偏冷狀態。")
    else:
        st.info("✅ 市場溫度中性。")

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3])
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="K線"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA50'], name="50天線"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA200'], name="200天線"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name="RSI"), row=2, col=1)
    fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
    
    fig.update_layout(height=500, xaxis_rangeslider_visible=False, margin=dict(l=10, r=10, t=30, b=10))
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"數據加載失敗: {e}")
