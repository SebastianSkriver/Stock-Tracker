import yfinance as yf
import smtplib
from email.mime.text import MIMEText
import pandas as pd
import schedule
import time

# Function to get the current stock price
def get_stock_price(symbol):
    stock = yf.Ticker(symbol)
    return stock.history(period="1d")['Close'].iloc[-1]

# Function to send an email notification
def send_email(subject, body, to_email):
    from_email = "Stock.Tracker.Python@gmail.com"  # Replace with your email
    password = "bdib awge zrjw dhnn"               # Replace with your email password

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(from_email, password)
        server.sendmail(from_email, to_email, msg.as_string())

# Function to check stock prices and send notifications
def check_stocks():
    watchlist = pd.read_csv("watchlist.csv")  # Load the watchlist
    for index, row in watchlist.iterrows():
        symbol = row['symbol']
        target_price = row['target_price']
        condition = row['condition']  # Get the condition (buy or sell)
        current_price = get_stock_price(symbol)

        print(f"{symbol}: Current Price = {current_price}, Target Price = {target_price}, Condition = {condition}")

        # Check the condition and trigger notifications accordingly
        if condition == "buy" and current_price <= target_price:
            subject = f"Stock Alert: {symbol} is at or below your buy target!"
            body = f"The current price of {symbol} is {current_price}, which is at or below your target price of {target_price}."
            send_email(subject, body, "bomskriver@gmail.com")  # Replace with recipient email

        elif condition == "sell" and current_price >= target_price:
            subject = f"Stock Alert: {symbol} is at or above your sell target!"
            body = f"The current price of {symbol} is {current_price}, which is at or above your target price of {target_price}."
            send_email(subject, body, "bomskriver@gmail.com")  # Replace with recipient email

# Schedule the script to run every hour
schedule.every(4).hour.do(check_stocks)

print("Stock tracker is running...")
while True:
    schedule.run_pending()
    time.sleep(1)

