import streamlit as st
from binance.client import Client

# Fetch Binance API keys securely from Streamlit secrets
def get_binance_client():
    try:
        # Access the API keys stored in Streamlit secrets
        api_key = st.secrets["binance"]["API_KEY"]
        api_secret = st.secrets["binance"]["API_SECRET"]
        return Client(api_key, api_secret)
    except KeyError:
        st.error("❌ Binance API keys not found in secrets.toml.")
        return None

def main():
    st.set_page_config(page_title="🔐 Secure Arbitrage Bot", page_icon="💸")
    st.title("💸 Binance Arbitrage Bot (Secure)")

    st.sidebar.header("⚙️ Configuration")
    trade_amount = st.sidebar.number_input("💰 Trade Amount (USDT)", min_value=1.0, value=50.0, step=10.0)
    threshold = st.sidebar.slider("📈 Profit Threshold (%)", min_value=1, max_value=30, value=5)

    # Test Binance connection
    if st.sidebar.button("🔌 Test Binance Connection"):
        client = get_binance_client()
        if client:
            try:
                # Ping Binance to check if the connection is working
                client.ping()
                account = client.get_account()  # Fetch account information
                usdt_balance = next((a for a in account['balances'] if a['asset'] == 'USDT'), None)
                st.success("✅ Successfully connected to Binance!")
                if usdt_balance:
                    st.info(f"💼 USDT Balance: {usdt_balance['free']} USDT")
            except Exception as e:
                st.error(f"❌ Connection failed: {e}")
        else:
            st.error("❌ Could not connect to Binance using the provided keys.")

    # Simulate auto-trading logic
    if st.sidebar.button("⚡ Start Auto-Trade Simulation"):
        st.success(f"Simulating trade of ${trade_amount} at threshold {threshold}%")
        st.info("🔁 (Auto-trade logic would run here. Extend this block to implement real trading.)")

    # Display footer information
    st.markdown("---")
    st.caption("🔒 Your API keys are safely loaded from Streamlit secrets (not in the code).")

if __name__ == "__main__":
    main()
