import streamlit as st
import plotly.graph_objects as go
from scanner import scan_market, get_market_data, add_indicators

st.title("🚀 AI Trading Scanner")

if st.button("🔍 Scansiona mercato"):
    results = scan_market()
    st.session_state["results"] = results

if "results" in st.session_state:
    st.subheader("🏆 Top Opportunità")

    for r in st.session_state["results"]:
        st.write(f"### {r['asset']}")
        st.write(f"Signal: {r['signal']}")
        st.write(f"Score: {r['score']}")

        if r["signal"] != "NO TRADE":
            st.write(f"Entry: {r['entry']}")
            st.write(f"SL: {r['sl']}")
            st.write(f"TP: {r['tp']}")

        st.markdown("---")

st.subheader("📊 Grafico")

symbol = st.selectbox("Scegli asset", [
    "BTC-USD","ETH-USD","AAPL","TSLA","EURUSD=X"
])

def plot_chart(symbol):
    data = get_market_data(symbol)
    data = add_indicators(data)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=data["Close"], name="Prezzo"))
    fig.add_trace(go.Scatter(x=data.index, y=data["ema50"], name="EMA50"))
    fig.add_trace(go.Scatter(x=data.index, y=data["ema200"], name="EMA200"))

    st.plotly_chart(fig)

plot_chart(symbol)
