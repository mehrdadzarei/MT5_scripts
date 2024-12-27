import yfinance as yf
import investpy
import requests
import pandas as pd
from datetime import datetime, timezone
import time
import MetaTrader5 as mt5
import dataProvider


symbols = [
    {"symbol": "NVDA"},
    {"symbol": "ASML.AS"},
    {"symbol": "TSLA"}
]


# # Fetch data from Bybit and prepare for MT5
# try:
#     kline_data = fetch_bybit_kline()
#     mt5_data = prepare_mt5_format(kline_data)
#     save_to_csv(mt5_data)
# except Exception as e:
#     print(f"Error: {e}")


# Collect data in a loop
# data_list = []
# for _ in range(5):  # Collect data 5 times (adjust as needed)
#     data = fetch_bitstamp_data()
#     data_list.append(data)
#     print(f"Collected: {data}")
#     time.sleep(60)  # Collect data every minute

# # Create a DataFrame
# df = pd.DataFrame(data_list)
# print(df)

# # Save the DataFrame to a CSV file compatible with MT5
# mt5_file = "BTCUSD_mt5.csv"
# df.to_csv(mt5_file, index=False, header=False)

# print(f"Data saved to {mt5_file}")

def save_to_mt5_format(data):
    with open(mt5_file, 'a') as f:
        f.write(f"{data['date']},{data['time']},{data['open']},{data['high']},{data['low']},{data['close']},{data['volume']}\n")



def fetch_stock_data_from_yfinance(symbol, interval="1m"):
    # Download data from Yahoo Finance
    data = yf.download(tickers=symbol, period="1d", interval=interval)
    return data

# # Example: Download historical data for EUR/USD
# data = investpy.get_currency_cross_historical_data(
#     currency_cross='EUR/USD',
#     from_date='01/01/2023',
#     to_date='31/12/2023',
#     interval='Daily'
# )

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

# symbol = "BTC-USD"  # Replace with your stock ticker
# stock_data = fetch_stock_data_from_yfinance(symbol)
# formatted_data = format_for_mt5(stock_data)
# print(formatted_data.head())

# # print last 5 rows of the data
# print(formatted_data.tail())


if __name__ == "__main__":
    
    data = dataProvider.DataProvider()
    # connect to MetaTrader 5
    if not data.connect_to_mt5():
        data.disconnect_from_mt5()
    else:

        
        yfinance_data = data.fetch_data(source="yfinance", symbol="NVDA", start=None, end=None, period="max", interval="1m")
        print(yfinance_data.head())
        print(yfinance_data.tail())



    data.disconnect_from_mt5()