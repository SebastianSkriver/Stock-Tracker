import tweepy
import yfinance as yf
import pandas as pd
import os

# Twitter API credentials from environment variables
TWITTER_API_KEY = os.getenv("TWITTER_API", "TZogagICUn8l1ShPCu3ITbg4N")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET", "7T0f1X0cOK9vXJKONf9t7fj872S6klMURGfvitm11fuQXkHkaQ")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS", "1879112447459483648-QJsj178fmkrA9ILi2jZsQi4RphlFbF")
TWITTER_ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET", "YZ6LT4ojuZaTmaC7ADGR7FVkiLiiTCqiDoJg7JxBS6epA")

# Authenticate with Twitter API using OAuth 1.0a
def authenticate_twitter():
    try:
        auth = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_API_SECRET)
        auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET)
        api = tweepy.API(auth)
        print("Twitter authentication successful.")
        return api
    except Exception as e:
        print(f"Error authenticating with Twitter: {e}")
        return None

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

# Post to Twitter using Tweepy
def post_to_twitter(api, tweet_lines):
    try:
        # Combine all lines into a single tweet (Twitter's character limit is 280)
        tweet_content = "\n".join(tweet_lines)
        if len(tweet_content) > 280:
            print("Tweet content exceeds 280 characters. Splitting into multiple tweets.")
            # Split into multiple tweets if necessary
            for i in range(0, len(tweet_lines), 5):  # Post 5 lines per tweet
                chunk = "\n".join(tweet_lines[i:i+5])
                api.update_status(chunk)
                print(f"Tweeted:\n{chunk}")
        else:
            # Post a single tweet
            api.update_status(tweet_content)
            print(f"Tweeted:\n{tweet_content}")
    except Exception as e:
        print(f"Error posting to Twitter: {e}")

# Main function
def main():
    # Authenticate with Twitter
    api = authenticate_twitter()
    if api is None:
        print("Twitter authentication failed. Exiting.")
        return

    # Generate tweet content
    csv_file = "Twitter_stock_list.csv"
    tweet_lines = generate_tweet_content(csv_file)

    # Post to Twitter
    if tweet_lines:
        post_to_twitter(api, tweet_lines)
    else:
        print("No data to tweet.")

if __name__ == "__main__":
    main()
