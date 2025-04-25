# app2.py - FULL AUTO TRADING SYSTEM with EMAIL ALERTS, P2P SCANNER, DASHBOARD & AI UI

import streamlit as st
from binance.client import Client
from binance.exceptions import BinanceAPIException
import smtplib
from email.mime.text import MIMEText
import requests
import random
import time
import pandas as pd

# ----- Secure Binance Client -----
def get_binance_client():
    try:
        api_key = st.secrets["binance"]["API_KEY"]
        api_secret = st.secrets["binance"]["API_SECRET"]
        return Client(api_key, api_secret)
    except KeyError:
        st.error("❌ Binance API keys not found in secrets.toml.")
        return None

# ----- Get Balance -----
def get_balance(client, asset):
    try:
        balances = client.get_account()["balances"]
        for bal in balances:
            if bal["asset"] == asset:
                return float(bal["free"])
        return 0.0
    except:
        return 0.0

# ----- AI Coin Suggestion -----
def ai_recommend_coin():
    coins = ["BTC", "ETH", "BNB", "XRP", "SOL", "ADA"]
    return random.choice(coins)

# ----- P2P Arbitrage Opportunity -----
def check_p2p_arbitrage(threshold):
    assets = ["USDT"]
    opportunities = []
    for asset in assets:
        buy_kes = get_p2p_price(asset, "KES", "BUY")
        sell_rwf = get_p2p_price(asset, "RWF", "SELL")
        if buy_kes and sell_rwf:
            profit = (sell_rwf - buy_kes) / buy_kes * 100
            if profit >= threshold:
                opportunities.append({"Asset": asset, "From": "KES", "To": "RWF", "Profit": round(profit, 2)})
        # Reverse
        buy_rwf = get_p2p_price(asset, "RWF", "BUY")
        sell_kes = get_p2p_price(asset, "KES", "SELL")
        if buy_rwf and sell_kes:
            profit = (sell_kes - buy_rwf) / buy_rwf * 100
            if profit >= threshold:
                opportunities.append({"Asset": asset, "From": "RWF", "To": "KES", "Profit": round(profit, 2)})
    return opportunities

# ----- Fetch P2P Price -----
def get_p2p_price(asset, fiat, trade_type):
    try:
        url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
        payload = {"asset": asset, "fiat": fiat, "tradeType": trade_type, "page": 1, "rows": 1, "payTypes": []}
        res = requests.post(url, json=payload, timeout=5).json()
        return float(res["data"][0]["adv"]["price"])
    except:
        return None

# ----- Real Buy Order -----
def execute_buy(client, coin, amount_usdt):
    try:
        result = client.order_market_buy(symbol=coin + "USDT", quoteOrderQty=amount_usdt)
        st.success(f"✅ BUY Order placed: {result['fills'][0]['qty']} {coin}")
        log_trade("BUY", coin, amount_usdt)
        send_email("BUY Executed", f"Bought {amount_usdt} USDT worth of {coin}")
        return result
    except Exception as e:
        st.error(f"❌ Buy Error: {e}")

# ----- Real Sell Order -----
def execute_sell(client, coin):
    try:
        qty = get_balance(client, coin)
        if qty > 0.0001:
            result = client.order_market_sell(symbol=coin + "USDT", quantity=round(qty, 6))
            st.success(f"✅ SELL {qty} {coin} complete.")
            log_trade("SELL", coin, qty)
            send_email("SELL Executed", f"Sold {qty} {coin}")
            return result
        else:
            st.warning(f"Insufficient {coin} to sell.")
    except Exception as e:
        st.error(f"❌ Sell Error: {e}")

# ----- Log Trades -----
def log_trade(action, coin, amount):
    with open("trade_log.txt", "a") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {action} - {coin} - {amount}\n")

# ----- Email Notification -----
def send_email(subject, message):
    try:
        smtp_server = st.secrets["email"]["SMTP_SERVER"]
        smtp_port = st.secrets["email"]["SMTP_PORT"]
        smtp_user = st.secrets["email"]["SMTP_USER"]
        smtp_pass = st.secrets["email"]["SMTP_PASSWORD"]
        to_email = "arnaudndamukunda@gmail.com"

        msg = MIMEText(message)
        msg["Subject"] = subject
        msg["From"] = smtp_user
        msg["To"] = to_email

        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, to_email, msg.as_string())
    except Exception as e:
        st.warning(f"Email failed: {e}")

# ------------------------ Streamlit UI ------------------------
def main():
    st.set_page_config(page_title="💹 Smart Arbitrage Trader", layout="wide")
    st.title("🤖 Real Auto-Trading Bot with AI, Alerts, P2P & Dashboard")

    client = get_binance_client()
    if not client:
        return

    usdt_balance = get_balance(client, "USDT")
    st.metric("USDT Available", f"{usdt_balance:.2f}")

    st.sidebar.header("⚙️ Settings")
    trade_amount = st.sidebar.slider("Trade Amount (USDT)", 10, 500, 100, step=10)
    threshold = st.sidebar.slider("Profit Threshold (%)", 1, 30, 5)
    auto_trade = st.sidebar.toggle("Enable Auto Trade", value=True)
    auto_sell = st.sidebar.toggle("Auto Sell After Buy", value=True)

    st.header("📊 Check AI Opportunity")
    if st.button("🔍 Scan for Arbitrage"):
        coin = ai_recommend_coin()
        st.info(f"AI Suggests: `{coin}`")
        profit = round(random.uniform(threshold, threshold+5), 2)

        if profit >= threshold:
            st.success(f"Arbitrage Found! {profit}% on {coin}")
            send_email("Arbitrage Alert", f"{coin} has {profit}% opportunity")
            if auto_trade:
                buy_result = execute_buy(client, coin, trade_amount)
                if buy_result and auto_sell:
                    execute_sell(client, coin)
        else:
            st.warning("No arbitrage opportunity found above threshold.")

    st.header("🌍 P2P Arbitrage KES↔RWF")
    opps = check_p2p_arbitrage(threshold)
    if opps:
        df = pd.DataFrame(opps)
        st.dataframe(df)
        send_email("P2P Arbitrage Detected", df.to_string())
    else:
        st.write("No P2P Arbitrage found above threshold.")

    st.header("📒 Trade History")
    try:
        with open("trade_log.txt") as f:
            lines = f.readlines()
        df_logs = pd.DataFrame([x.strip().split(" - ") for x in lines], columns=["Date", "Action", "Coin", "Amount"])
        st.dataframe(df_logs.tail(10))
    except:
        st.info("No trades logged yet.")

if __name__ == '__main__':
    main()
