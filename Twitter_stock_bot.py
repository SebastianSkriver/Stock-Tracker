import requests
import yfinance as yf
import pandas as pd
import os

# Twitter API credentials from environment variables
TWITTER_BEARER = os.getenv("TWITTER_BEARER")

# Fetch stock prices
def fetch_stock_price(stock_symbol):
    try:
        stock = yf.Ticker(stock_symbol)
        stock_data = stock.history(period="1d")
        current_price = stock_data["Close"].iloc[-1]
        return current_price
    except Exception as e:
        print(f"Error fetching price for {stock_symbol}: {e}")
        return None

# Generate recommendations and format tweet content
def generate_tweet_content(csv_file):
    tweet_lines = []
    try:
        # Read the CSV file
        df = pd.read_csv(csv_file)
        for index, row in df.iterrows():
            stock = row["Stock"]
            buy_target = row["Buy_Target"]
            sell_target = row["Sell_Target"]

            # Fetch the current stock price
            current_price = fetch_stock_price(stock)
            if current_price is None:
                continue

            # Determine recommendation
            if current_price < buy_target:
                action = "Buy"
            elif current_price > sell_target:
                action = "Sell"
            else:
                action = "Wait"

            # Format the tweet line
            tweet_line = f"{stock}: ${current_price:.2f} | Action: {action} (Buy: ${buy_target}, Sell: ${sell_target})"
            tweet_lines.append(tweet_line)
    except Exception as e:
        print(f"Error generating tweet content: {e}")
    return tweet_lines

# Post to Twitter using API v2
def post_to_twitter_v2(tweet_lines):
    try:
        # Twitter API v2 endpoint
        url = "https://api.twitter.com/2/tweets"
        headers = {
            "Authorization": f"Bearer {TWITTER_BEARER}",
            "Content-Type": "application/json"
        }

        # Combine all lines into a single tweet (Twitter's character limit is 280)
        tweet_content = "\n".join(tweet_lines)
        if len(tweet_content) > 280:
            print("Tweet content exceeds 280 characters. Splitting into multiple tweets.")
            # Split into multiple tweets if necessary
            for i in range(0, len(tweet_lines), 5):  # Post 5 lines per tweet
                chunk = "\n".join(tweet_lines[i:i+5])
                payload = {"text": chunk}
                response = requests.post(url, headers=headers, json=payload)
                if response.status_code == 201:
                    print(f"Tweeted:\n{chunk}")
                else:
                    print(f"Error posting tweet: {response.status_code} - {response.text}")
        else:
            # Post a single tweet
            payload = {"text": tweet_content}
            response = requests.post(url, headers=headers, json=payload)
            if response.status_code == 201:
                print(f"Tweeted:\n{tweet_content}")
            else:
                print(f"Error posting tweet: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error posting to Twitter: {e}")

# Main function
def main():
    # Generate tweet content
    csv_file = "Twitter_stock_list.csv"
    tweet_lines = generate_tweet_content(csv_file)

    # Post to Twitter
    if tweet_lines:
        post_to_twitter_v2(tweet_lines)
    else:
        print("No data to tweet.")

if __name__ == "__main__":
    main()
