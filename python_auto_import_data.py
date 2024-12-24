import yfinance as yf
import pandas as pd
import MetaTrader5 as mt5

def fetch_stock_data(symbol, interval="1m"):
    # Download data from Yahoo Finance
    data = yf.download(tickers=symbol, period="1d", interval=interval)
    return data

def format_for_mt5(data):
    # Format data for MT5 (Time, Open, High, Low, Close, Volume)
    data.reset_index(inplace=True)
    data = data.rename(columns={
        "Datetime": "Time", 
        "Open": "Open", 
        "High": "High", 
        "Low": "Low", 
        "Close": "Close", 
        "Volume": "Volume"
    })
    return data

symbol = "ASML"  # Replace with your stock ticker
stock_data = fetch_stock_data(symbol)
formatted_data = format_for_mt5(stock_data)
print(formatted_data.head())
