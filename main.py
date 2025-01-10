import yfinance as yf
import pandas as pd
import pandas_ta as ta
from collections import Counter
import json 

with open('stocks.json', 'r') as file:
    stocks = json.load(file)

def fetch_data(symbol, interval='1h', period='5d'):
    data = yf.download(tickers=symbol, interval=interval, period=period)
    if not data.empty:
        data.reset_index(inplace=True)
        data.rename(columns={"Open": "open", "High": "high", "Low": "low", "Close": "close", "Volume": "volume"}, inplace=True)
    return data

def compute_indicators(data):
    if len(data) < 14:
        data['RSI'] = None
    else:
        data['RSI'] = ta.rsi(data['close'], length=14)
    return data

def check_divergence(data):
    if len(data) < 2:
        return False, False

    low1, low2 = data['low'].iloc[-2], data['low'].iloc[-1]
    high1, high2 = data['high'].iloc[-2], data['high'].iloc[-1]
    rsi1, rsi2 = data['RSI'].iloc[-2], data['RSI'].iloc[-1]

    bullish_divergence = low2 < low1 and rsi2 > rsi1
    bearish_divergence = high2 > high1 and rsi2 < rsi1

    return bullish_divergence, bearish_divergence

def get_recommendation(data):
    if data['RSI'].isnull().all():  
        return "HOLD"

    bullish_divergence, bearish_divergence = check_divergence(data)

    if bullish_divergence:
        return "BUY"

    elif bearish_divergence:
        return "SELL"

    else:
        return "HOLD"

def main():
    recommendations_by_stock = {}

    for stock in stocks:
        print(f"Analyzing {stock}...")
        try:
            data = fetch_data(stock)
            if data.empty:
                print(f"Error analyzing {stock}: No data available.")
                continue

            data = compute_indicators(data)
            recommendation = get_recommendation(data)

            if recommendation != "HOLD":
                recommendations_by_stock[stock] = recommendation

        except Exception as e:
            print(f"Error analyzing {stock}: {e}")
            continue

    sorted_recommendations = sorted(recommendations_by_stock.items(), key=lambda x: x[1], reverse=True)

    print("\nPopular Opinion for each Stock (Sorted):")
    for stock, recommendation in sorted_recommendations:
        print(f"{stock}: {recommendation}")

if __name__ == "__main__":
    main()
