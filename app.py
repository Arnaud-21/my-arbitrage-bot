# app.py - Binance KES↔RWF Arbitrage Dashboard with Real P2P Auto-Trade and Connection Test
# 📦 Requirements:
# pip install streamlit python-binance requests

import os
import time
import json
import requests
import streamlit as st
from binance.client import Client

# ---------------------------
# Configuration
# ---------------------------
API_KEY = os.getenv("BINANCE_API_KEY", "YuvuoQ4CTmPVDTioFAyUcGYZweWFC5SRVpe4uCDOVGX72sph2j2XCEGZT0aVpgP9")
API_SECRET = os.getenv("BINANCE_API_SECRET", "jsZ6DAd5aYdOrqCoKg8Fnlkf5z5jxGmIiUT9gcZU4Go0VPEnk3FzxWwsmVnvKkH9")
client = Client(API_KEY, API_SECRET)

# ---------------------------
# Helper Functions
# ---------------------------
@st.cache_data(ttl=60)
def get_price(asset, fiat, trade_type):
    """
    Fetch P2P price and advertisement details.
    Returns: price(float), advNo(str), tradeMethods(list)
    """
    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    payload = {"asset": asset, "fiat": fiat, "tradeType": trade_type, "page": 1, "rows": 1, "payTypes": []}
    try:
        res = requests.post(url, json=payload, timeout=5).json()
        adv = res["data"][0]["adv"]
        price = float(adv["price"])
        advNo = adv["advNo"]
        methods = adv.get("tradeMethods", [])
        return price, advNo, methods
    except Exception:
        return None, None, []


def find_arbitrage(threshold):
    """
    Identify arbitrage opportunities above the given profit threshold.
    """
    ASSETS = ["USDT","BTC","ETH","BNB","BUSD","XRP","ADA","SOL","DOT"]
    usdt_kes, _, _ = get_price("USDT", "KES", "BUY") or (1, None, [])
    usdt_rwf, _, _ = get_price("USDT", "RWF", "BUY") or (1, None, [])
    rate = usdt_rwf / usdt_kes
    opps = []

    for asset in ASSETS:
        # KES → RWF
        buy, buyAdv, buyMethods = get_price(asset, "KES", "BUY")
        sell, sellAdv, sellMethods = get_price(asset, "RWF", "SELL")
        if buy and sell:
            profit = (sell - buy * rate) / (buy * rate) * 100
            if profit >= threshold:
                opps.append({
                    "Asset": asset,
                    "Direction": "KES→RWF",
                    "BuyPrice": buy,
                    "SellPrice": sell,
                    "Profit": round(profit, 2),
                    "BuyAdv": buyAdv,
                    "SellAdv": sellAdv,
                    "BuyMethods": buyMethods,
                    "SellMethods": sellMethods
                })
        # RWF → KES
        buy, buyAdv, buyMethods = get_price(asset, "RWF", "BUY")
        sell, sellAdv, sellMethods = get_price(asset, "KES", "SELL")
        if buy and sell:
            profit = (sell - buy / rate) / (buy / rate) * 100
            if profit >= threshold:
                opps.append({
                    "Asset": asset,
                    "Direction": "RWF→KES",
                    "BuyPrice": buy,
                    "SellPrice": sell,
                    "Profit": round(profit, 2),
                    "BuyAdv": buyAdv,
                    "SellAdv": sellAdv,
                    "BuyMethods": buyMethods,
                    "SellMethods": sellMethods
                })
    return opps


def place_p2p_order(advNo, tradeType, asset, fiat, amount, payTypes):
    """
    Place a real P2P order via Binance's friendly endpoint.
    payTypes: list of payType strings e.g. ["M-PESA"]
    """
    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/order/place"
    payload = {
        "advNo": advNo,
        "tradeType": tradeType,
        "asset": asset,
        "fiat": fiat,
        "amount": str(amount),
        "payTypes": payTypes
    }
    headers = {"Content-Type": "application/json"}
    resp = requests.post(url, json=payload, headers=headers, timeout=10)
    try:
        return resp.json()
    except ValueError:
        return {"error": resp.text}

# ---------------------------
# Streamlit UI
# ---------------------------
st.set_page_config(page_title="Binance Arbitrage", layout="wide")
st.title("🔍 Binance KES↔RWF Arbitrage Dashboard")

# Sidebar controls
st.sidebar.header("⚙️ Settings")
threshold = st.sidebar.slider("Profit Threshold (%)", 1, 30, 3)
volume = st.sidebar.selectbox("Trade Volume (fiat)", [10, 20, 50, 100, 200, 500], index=2)
auto_trade = st.sidebar.checkbox("Enable Auto-Trade", value=False)

# Test Binance connection
if st.sidebar.button("🔌 Test Connection"):
    try:
        client.ping()
        st.sidebar.success("✅ Connected to Binance API!")
        account = client.get_account()
        usdt_bal = next((b for b in account['balances'] if b['asset']=='USDT'), {})
        st.sidebar.write(f"**USDT Balance:** {usdt_bal.get('free','0')} free / {usdt_bal.get('locked','0')} locked")
    except Exception as e:
        st.sidebar.error(f"❌ Connection failed: {e}")

if st.sidebar.button("🔄 Refresh Data"):
    st.experimental_rerun()

# Display current settings
st.markdown(f"**Threshold:** {threshold}%   **Volume:** {volume}   **Auto-Trade:** {'On' if auto_trade else 'Off'}")
st.markdown("---")

# Fetch and display opportunities
t0 = time.time()
opps = find_arbitrage(threshold)
t1 = time.time()
st.write(f"Fetched in {t1 - t0:.2f}s")

if not opps:
    st.info("No arbitrage opportunities above threshold.")
else:
    for op in opps:
        st.subheader(f"{op['Asset']} — {op['Direction']} — {op['Profit']}%")
        st.write(f"Buy @ {op['BuyPrice']} → Sell @ {op['SellPrice']}")
        if auto_trade:
            buyPay = [m['payType'] for m in op['BuyMethods']] if op['BuyMethods'] else []
            sellPay = [m['payType'] for m in op['SellMethods']] if op['SellMethods'] else []
            buyRes = place_p2p_order(op['BuyAdv'], 'BUY', op['Asset'], op['Direction'].split('→')[0], volume, buyPay)
            sellRes = place_p2p_order(op['SellAdv'], 'SELL', op['Asset'], op['Direction'].split('→')[1], volume, sellPay)
            st.success("🟢 Auto-Trade executed")
            st.json({"BuyResponse": buyRes, "SellResponse": sellRes})
        st.markdown("---")

# End of app.py
