import streamlit as st
from binance.client import Client

# 🚨 DIRECTLY INCLUDED API KEYS (for private testing ONLY)
API_KEY = "YuvuoQ4CTmPVDTioFAyUcGYZweWFC5SRVpe4uCDOVGX72sph2j2XCEGZT0aVpgP9"
API_SECRET = "jsZ6DAd5aYdOrqCoKg8Fnlkf5z5jxGmIiUT9gcZU4Go0VPEnk3FzxWwsmVnvKkH9"

# Initialize Binance client using hardcoded keys
def get_binance_client():
    return Client(API_KEY, API_SECRET)

# Main Streamlit app
def main():
    st.set_page_config(page_title="Arbitrage Bot", page_icon="💸")
    st.title("💸 Binance Arbitrage Bot")
    st.markdown("Use this interface to monitor and simulate arbitrage opportunities using your Binance account.")

    st.sidebar.header("🔧 Configuration")

    # Inputs for trading settings
    trade_amount = st.sidebar.number_input("💰 Trade Amount (USDT)", min_value=1.0, value=50.0, step=10.0)
    threshold = st.sidebar.slider("📈 Profit Threshold (%)", min_value=1, max_value=30, value=5)

    # Test Binance API connection
    if st.sidebar.button("🔌 Test Binance Connection"):
        try:
            client = get_binance_client()
            client.ping()
            account_info = client.get_account()
            balances = account_info['balances']
            usdt_balance = next((b for b in balances if b['asset'] == 'USDT'), None)
            st.success("✅ Successfully connected to Binance!")
            if usdt_balance:
                st.info(f"💼 USDT Balance: {usdt_balance['free']} USDT")
        except Exception as e:
            st.error(f"❌ Connection failed: {e}")

    # Simulate auto-trading logic
    if st.sidebar.button("⚡ Start Auto-Trade Simulation"):
        st.sidebar.success(f"Simulated Trade for {trade_amount} USDT at {threshold}% threshold")
        st.info("🔁 This is a simulation. Auto-trade logic would execute real trades if enabled.")

    # Display footer
    st.markdown("---")
    st.markdown("🔒 *Note: API keys are embedded for private use only. Remove before sharing or deploying.*")

if __name__ == "__main__":
    main()
