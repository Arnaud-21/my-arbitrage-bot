import streamlit as st
from binance.client import Client
from binance.exceptions import BinanceAPIException
import random

# ⛓️ Connect to Binance API
def get_binance_client():
    try:
        api_key = st.secrets["binance"]["API_KEY"]
        api_secret = st.secrets["binance"]["API_SECRET"]
        return Client(api_key, api_secret)
    except KeyError:
        st.error("❌ Binance API keys not found in secrets.toml.")
        return None
    except Exception as e:
        st.error(f"❌ Unexpected error loading API keys: {e}")
        return None

# 💰 Get USDT balance
def get_usdt_balance(client):
    try:
        account = client.get_account()
        for asset in account['balances']:
            if asset['asset'] == 'USDT':
                return float(asset['free'])
    except:
        return None

# 📈 Generate mock arbitrage opportunity (simulate only)
def find_mock_arbitrage(amount, threshold):
    profit_pct = round(random.uniform(threshold, threshold + 3), 2)
    estimated_profit = round(amount * profit_pct / 100, 2)
    coin = random.choice(["BTC", "ETH", "BNB", "XRP", "SOL"])
    return {
        "coin": coin,
        "profit_pct": profit_pct,
        "estimated_profit": estimated_profit,
        "direction": random.choice(["KES → RWF", "RWF → KES"])
    }

# 🚀 Main app logic
def main():
    st.set_page_config(page_title="Arbitrage Bot", layout="wide", page_icon="💹")
    st.title("💹 East Africa Crypto Arbitrage Monitor")

    st.sidebar.header("🔧 Settings")

    # 🔌 Connect to Binance
    if st.sidebar.button("🔌 Test Binance Connection"):
        client = get_binance_client()
        if client:
            try:
                client.ping()
                st.sidebar.success("✅ Connected to Binance!")
                usdt = get_usdt_balance(client)
                if usdt is not None:
                    st.success(f"💰 Your USDT Balance: {usdt:.2f}")
            except BinanceAPIException:
                st.sidebar.error("❌ Binance API error. Check permissions or IP restrictions.")
            except Exception as e:
                st.sidebar.error(f"❌ Connection error: {e}")
        else:
            st.sidebar.error("⚠️ Client creation failed.")

    # ⚙️ Trade configuration
    st.sidebar.markdown("---")
    trade_amount = st.sidebar.slider("💵 Amount to Trade (USDT)", 10, 1000, 100, step=10)
    threshold = st.sidebar.slider("📈 Profit Threshold (%)", 1, 30, 5)

    auto_trade = st.sidebar.toggle("🧠 Enable Auto-Trade (Simulated)")

    st.markdown(f"""
    **Trade Amount:** `{trade_amount} USDT`  
    **Profit Threshold:** `{threshold}%`  
    **Auto-Trade Enabled:** `{auto_trade}`
    """)

    st.markdown("---")

    st.subheader("📊 Simulated Arbitrage Opportunities")

    # 🔍 Simulated Opportunity
    mock_op = find_mock_arbitrage(trade_amount, threshold)
    st.success(f"📈 Potential Arbitrage on {mock_op['coin']} - {mock_op['direction']}")
    st.write(f"💰 Estimated Profit: `{mock_op['estimated_profit']} USDT`")
    st.write(f"📊 Profit Margin: `{mock_op['profit_pct']}%`")

    if auto_trade:
        st.info("✅ Auto-trade logic would be executed here.")
    else:
        st.warning("🔕 Auto-trade is disabled. Enable it from the sidebar to simulate execution.")

    st.caption("Note: This is a simulation. Real trading logic will be added soon.")

if __name__ == "__main__":
    main()
