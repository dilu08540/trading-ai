import yfinance as yf
import pandas as pd
import numpy as np
from ta.momentum import RSIIndicator

ASSETS = [
    "BTC-USD","ETH-USD","SOL-USD","BNB-USD","XRP-USD","ADA-USD",
    "AAPL","MSFT","NVDA","GOOGL","AMZN","META","TSLA",
    "JPM","BAC",
    "CL=F","GC=F",
    "EURUSD=X","GBPUSD=X","USDJPY=X",
    "ENEL.MI","ENI.MI","ISP.MI",
    "^GSPC","^IXIC"
]

ASSET_PROFILES = {
    "crypto": {"rsi_buy": 35, "rsi_sell": 65, "volatility": 1.05},
    "stocks": {"rsi_buy": 30, "rsi_sell": 70, "volatility": 1.03},
    "forex": {"rsi_buy": 40, "rsi_sell": 60, "volatility": 1.01}
}

def get_asset_type(symbol):
    if "USD" in symbol and "-" in symbol:
        return "crypto"
    elif "USD=X" in symbol:
        return "forex"
    else:
        return "stocks"

def get_market_data(symbol):
    data = yf.download(symbol, period="7d", interval="1h")
    data.dropna(inplace=True)
    return data

def add_indicators(data):
    data["rsi"] = RSIIndicator(data["Close"]).rsi()
    data["ema50"] = data["Close"].ewm(span=50).mean()
    data["ema200"] = data["Close"].ewm(span=200).mean()
    return data

def get_trend(data):
    last = data.iloc[-1]
    if last["ema50"] > last["ema200"]:
        return "bullish"
    elif last["ema50"] < last["ema200"]:
        return "bearish"
    return "sideways"

def generate_signal(data, trend, asset_type):
    profile = ASSET_PROFILES[asset_type]
    last = data.iloc[-1]

    rsi = last["rsi"]
    price = last["Close"]

    if trend == "bullish" and rsi < profile["rsi_buy"]:
        return {"signal":"BUY","entry":price,
                "sl":price*(1-0.02*profile["volatility"]),
                "tp":price*(1+0.04*profile["volatility"])}

    elif trend == "bearish" and rsi > profile["rsi_sell"]:
        return {"signal":"SELL","entry":price,
                "sl":price*(1+0.02*profile["volatility"]),
                "tp":price*(1-0.04*profile["volatility"])}

    return {"signal":"NO TRADE"}

def score_trade(signal, rsi, trend, data):
    if signal["signal"] == "NO TRADE":
        return 0

    score = 0

    ema_diff = abs(data.iloc[-1]["ema50"] - data.iloc[-1]["ema200"])
    score += min(ema_diff * 100, 40)

    rsi_score = abs(50 - rsi)
    score += min(rsi_score, 30)

    volatility = data["Close"].pct_change().std()
    score += min(volatility * 1000, 30)

    return round(min(score, 100), 2)

def scan_market():
    results = []

    for symbol in ASSETS:
        data = get_market_data(symbol)
        data = add_indicators(data)

        trend = get_trend(data)
        asset_type = get_asset_type(symbol)

        signal = generate_signal(data, trend, asset_type)
        rsi = data.iloc[-1]["rsi"]

        score = score_trade(signal, rsi, trend, data)

        signal["score"] = score
        signal["asset"] = symbol

        results.append(signal)

    ranked = sorted(results, key=lambda x: x["score"], reverse=True)
    return ranked
