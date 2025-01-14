import yfinance as yf
import csv
from mastodon import Mastodon
import os

# Function to fetch stock prices
def fetch_stock_prices(stock_symbols):
    stock_data = {}
    for symbol in stock_symbols:
        try:
            stock = yf.Ticker(symbol)
            stock_info = stock.history(period="1d")
            if not stock_info.empty:
                current_price = stock_info['Close'].iloc[-1]
                stock_data[symbol] = current_price
            else:
                stock_data[symbol] = None
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            stock_data[symbol] = None
    return stock_data

# Function to analyze stock prices against target prices
def analyze_stocks(stock_data, target_prices):
    recommendations = []
    for symbol, current_price in stock_data.items():
        if current_price is None:
            recommendations.append(f"{symbol}: No data available")
            continue
        target_buy = target_prices.get(symbol, {}).get("buy")
        target_sell = target_prices.get(symbol, {}).get("sell")
        if target_buy and current_price <= target_buy:
            recommendations.append(f"{symbol}: Buy (Current: ${current_price:.2f}, Target: ${target_buy:.2f})")
        elif target_sell and current_price >= target_sell:
            recommendations.append(f"{symbol}: Sell (Current: ${current_price:.2f}, Target: ${target_sell:.2f})")
        else:
            recommendations.append(f"{symbol}: Wait (Current: ${current_price:.2f})")
    return recommendations

# Function to post updates to Mastodon
def post_to_mastodon(recommendations):
    try:
        # Authenticate with Mastodon
        mastodon = Mastodon(
            client_id=os.getenv("MASTADON_CLIENT_KEY"),
            client_secret=os.getenv("MASTADON_CLIENT_SECRET"),
            access_token=os.getenv("MASTADON_ACCESS_TOKEN"),
            api_base_url="https://mastodon.social"  # Change this if you're using a different instance
        )

        # Combine recommendations into a single post
        post_content = "\n".join(recommendations)
        if len(post_content) > 500:  # Mastodon character limit is 500
            print("Post content exceeds 500 characters. Splitting into multiple posts.")
            for i in range(0, len(recommendations), 10):  # Post 10 recommendations per post
                chunk = "\n".join(recommendations[i:i+10])
                mastodon.toot(chunk)
        else:
            mastodon.toot(post_content)
        print("Successfully posted to Mastodon!")
    except Exception as e:
        print(f"Error posting to Mastodon: {e}")

# Main function
def main():
    # Load stock symbols and target prices from CSV
    stock_symbols = []
    target_prices = {}
    try:
        with open("Twitter_stock_list.csv", "r") as file:
            reader = csv.DictReader(file)
            print("CSV Headers:", reader.fieldnames)  # Debugging: Print the headers
            for row in reader:
                print("Row:", row)  # Debugging: Print each row
                symbol = row["Symbol"]
                stock_symbols.append(symbol)
                target_prices[symbol] = {
                    "buy": float(row["Buy_Target"]) if row["Buy_Target"] else None,
                    "sell": float(row["Sell_Target"]) if row["Sell_Target"] else None,
                }
    except FileNotFoundError:
        print("Error: CSV file not found.")
        return
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return

    # Fetch stock prices
    stock_data = fetch_stock_prices(stock_symbols)

    # Analyze stock prices
    recommendations = analyze_stocks(stock_data, target_prices)

    # Post recommendations to Mastodon
    post_to_mastodon(recommendations)

if __name__ == "__main__":
    main()
