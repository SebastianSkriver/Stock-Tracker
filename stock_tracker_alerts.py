import os
import yfinance as yf
import smtplib
from email.mime.text import MIMEText
import pandas as pd

# Function to get the current stock price
def get_stock_price(symbol):
    stock = yf.Ticker(symbol)
    return stock.history(period="1d")['Close'].iloc[-1]

# Function to send an email notification
def send_email(subject, body):
    # Fetch email credentials from environment variables
    from_email = os.getenv("EMAIL")  # Your email address
    password = os.getenv("EMAIL_PASSWORD")  # Your email password

    # Check if environment variables are set
    if not from_email or not password:
        raise ValueError("EMAIL and EMAIL_PASSWORD environment variables must be set.")

    # Set the recipient email
    to_email = os.getenv("EMAIL")

    # Create the email message
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email

    # Send the email
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(from_email, password)
            server.sendmail(from_email, to_email, msg.as_string())
        print(f"Email sent successfully to {to_email} with subject: {subject}")
    except Exception as e:
        print(f"Failed to send email: {e}")

# Function to check stock prices and send notifications
def check_stocks():
    # Load the watchlist
    try:
        watchlist = pd.read_csv("watchlist.csv")
        print("Watchlist loaded successfully:")
        print(watchlist)
    except Exception as e:
        print(f"Error loading watchlist.csv: {e}")
        return

    # Process each stock in the watchlist
    for index, row in watchlist.iterrows():
        symbol = row['symbol']
        target_price = row['target_price']
        condition = row['condition']  # Get the condition (buy or sell)
        try:
            current_price = get_stock_price(symbol)
            print(f"{symbol}: Current Price = {current_price}, Target Price = {target_price}, Condition = {condition}")

            # Check the condition and trigger notifications accordingly
            if condition == "buy" and current_price <= target_price:
                subject = f"Stock Alert: {symbol} is at or below your buy target!"
                body = f"The current price of {symbol} is {current_price}, which is at or below your target price of {target_price}."
                send_email(subject, body)

            elif condition == "sell" and current_price >= target_price:
                subject = f"Stock Alert: {symbol} is at or above your sell target!"
                body = f"The current price of {symbol} is {current_price}, which is at or above your target price of {target_price}."
                send_email(subject, body)

        except Exception as e:
            print(f"Error processing stock {symbol}: {e}")

# Run the stock check function
if __name__ == "__main__":
    check_stocks()
