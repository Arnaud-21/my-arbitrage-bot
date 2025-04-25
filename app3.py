import streamlit as st
import toml
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from binance.client import Client
import time

# Load API keys and email credentials from secrets.toml
config = toml.load("secrets.toml")

# Binance API Setup
binance_api_key = config['binance']['API_KEY']
binance_api_secret = config['binance']['API_SECRET']
client = Client(binance_api_key, binance_api_secret)

# Email Setup
smtp_server = config['email']['SMTP_SERVER']
smtp_port = config['email']['SMTP_PORT']
smtp_user = config['email']['SMTP_USER']
smtp_password = config['email']['SMTP_PASSWORD']

# Function to send email alerts
def send_email(subject, body, to_email):
    msg = MIMEMultipart()
    msg['From'] = smtp_user
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        server.login(smtp_user, smtp_password)
        text = msg.as_string()
        server.sendmail(smtp_user, to_email, text)
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")

# Function to get Binance market data and detect arbitrage
def check_arbitrage_opportunities():
    # Fetch all Binance markets
    markets = client.get_all_tickers()

    arbitrage_opportunities = []
    
    # Check for arbitrage opportunities (simplified example)
    for market in markets:
        symbol = market['symbol']
        if 'USDT' in symbol:  # Look for pairs with USDT
            price = float(market['price'])
            if price > 1:  # Arbitrary condition for illustration
                arbitrage_opportunities.append({
                    'symbol': symbol,
                    'price': price
                })
    
    return arbitrage_opportunities

# Streamlit Interface
st.title("Binance Arbitrage Scanner")

# Display a loading message
st.write("Loading Binance market data and checking for arbitrage opportunities...")

# Periodically check for arbitrage
while True:
    arbitrage_opportunities = check_arbitrage_opportunities()

    if arbitrage_opportunities:
        st.write("Arbitrage Opportunities Found!")
        for opportunity in arbitrage_opportunities:
            st.write(f"Symbol: {opportunity['symbol']} - Price: {opportunity['price']}")

            # Send email alert for each opportunity
            email_subject = f"Arbitrage Opportunity: {opportunity['symbol']}"
            email_body = f"Arbitrage Opportunity detected! Symbol: {opportunity['symbol']} - Price: {opportunity['price']}"
            send_email(email_subject, email_body, smtp_user)

        # Display a message
        st.write("Arbitrage opportunities sent via email.")
    else:
        st.write("No arbitrage opportunities found at the moment.")

    # Wait before checking again (e.g., every 60 seconds)
    time.sleep(60)
