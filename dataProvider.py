"""dataProvider.py contains getting data from differen data providers and 
converting them to the MT5 format.

"""

import yfinance as yf
import investpy
import requests
import pandas as pd
from datetime import datetime, timezone
import time
import MetaTrader5 as mt5


class MT5_funcs:
    def __init__(self):
        self.path = "C:\\Program Files\\MetaTrader 5\\terminal64.exe"

    def connect_to_mt5(self, loginN = None, passw = "", serverN = ""):
        # connect to MetaTrader 5
        if not mt5.initialize(self.path):
            print("initialize() failed, error code =", mt5.last_error())
            return False
        elif loginN is not None:
            # switch account seperatly to avoid error during first initialization
            if not mt5.initialize(login=loginN, password=passw, server=serverN):
                print("switch account failed, error code =", mt5.last_error())
                return False
        
        return True

    def disconnect_from_mt5(self):
        mt5.shutdown()
    
    # Insert data into MT5
    def import_data_to_mt5(symbol, data):
        for _, row in data.iterrows():
            rates = mt5.CopyRatesFromPos(symbol, mt5.TIMEFRAME_M1, 0, len(data))
            new_rate = {
                "time": int(row["time"].timestamp()),
                "open": row["open"],
                "high": row["high"],
                "low": row["low"],
                "close": row["close"],
                "tick_volume": row["volume"],
                "spread": 0,
                "real_volume": 0
            }
            rates.append(new_rate)

            if not mt5.symbol_set(symbol, rates):
                print(f"Failed to import data for {symbol}")
                break

class DataProvider(MT5_funcs):
    def __init__(self):
        super().__init__()
        # Bybit API Endpoint for K-line data
        self.bybit_url = "https://api.bybit.com/v2/public/kline/list"
        # Bitstamp API URL for BTC/USD ticker
        self.bitstamp_url = "https://www.bitstamp.net/api/v2/ticker/btcusd/"

    def prepare_mt5_format(self, data):
        """
        Prepare the data in MT5-compatible format.
        """
        # mt5_data = []
        # for candle in data:
            # timestamp = candle["open_time"]
            # dt = datetime.utcfromtimestamp(timestamp)
            # date = dt.strftime('%Y.%m.%d')
            # time = dt.strftime('%H:%M')
            # open_price = float(candle["open"])
            # high_price = float(candle["high"])
            # low_price = float(candle["low"])
            # close_price = float(candle["close"])
            # volume = float(candle["volume"])
            # mt5_data.append([date, time, open_price, high_price, low_price, close_price, volume])
        
        

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

    def save_to_csv(self, data, filename="BTCUSD_m1_mt5.csv"):
        """
        Save the MT5-compatible data to a CSV file.
        """
        # df = pd.DataFrame(data, columns=["Date", "Time", "Open", "High", "Low", "Close", "Volume"])
        # print(df.tail())
        # df.to_csv(f"../data/{filename}", index=False, header=False)
        data.to_csv(f"C:/Users/mzarei/AppData/Roaming/MetaQuotes/Terminal/D0E8209F77C8CF37AD8BF550E51FF075/MQL5/Files/data/{filename}", index=False)
        print(f"Data saved to {filename}")

    def get_symbol_info(self, symbol):
        ticker = yf.Ticker(symbol)
        info = ticker.info
        print(f"Name: {info.get('symbol')}")
        print(f"Currency: {info.get('currency')}")
        print(f"Digits: {info.get('regularMarketPrice')}")
        # return {
        #     "Name": info.get("symbol"),
        #     "Currency": info.get("currency"),
        #     "Digits": 2 if info.get("regularMarketPrice") < 100 else 5,
        #     "TickSize": 0.01,
        #     "ContractSize": 1,
        #     "MinVolume": 1,
        #     "MaxVolume": 100,
        #     "VolumeStep": 1
        # }
    
    def fetch_yfinance_data(self, symbol="ASML", start=None, end=None, period="max", interval="1m"):
        """
        Fetch historical data from Yahoo Finance using yfinance.
        """
        data = yf.download(tickers=symbol, start=start, end=end, period=period, interval=interval)
        print(data.head())
        return data

    def fetch_bybit_kline(self, symbol="BTCUSD", interval="1", limit=200):
        """
        Fetch 1-minute candlestick data from Bybit.
        """
        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": limit  # Number of candles to fetch
        }
        response = requests.get(self.bybit_url, params=params)
        data = response.json()
        if "result" in data:
            return data["result"]
        else:
            raise ValueError(f"Error fetching data: {data}")

    def fetch_bitstamp_data(self):
        response = requests.get(self.bitstamp_url)
        data = response.json()
        # Use timezone-aware datetime
        dt = datetime.fromtimestamp(int(data['timestamp']), tz=timezone.utc)
        return {
            "date": dt.strftime('%Y.%m.%d'),
            "time": dt.strftime('%H:%M'),
            "open": float(data['open']),
            "high": float(data['high']),
            "low": float(data['low']),
            "close": float(data['last']),
            "volume": float(data['volume'])
        }
    
    def fetch_investpy_data(self, symbol="BTC/USD", start="01/01/2021", end="31/01/2021"):
        """
        Fetch historical data from Investing.com using investpy
        """

    def fetch_data(self, source = "yfinance", symbol="NVDA", start=None, end=None, period="max", interval="1m", limit=200):
        """
        Fetch data from different providers and prepare for MT5.
        """
        if source == "yfinance":
            data = self.fetch_yfinance_data(symbol, start, end, period, interval)
            mt5_data = self.prepare_mt5_format(data)
            self.save_to_csv(mt5_data, f"{symbol}_{interval}_mt5.csv")
        elif source == "bybit":
            kline_data = self.fetch_bybit_kline(symbol, interval, limit)
            mt5_data = self.prepare_mt5_format(kline_data)
            print(mt5_data[:5])
            print(mt5_data[-5:])
        else:
            raise ValueError("Invalid source specified.")
        

        # # Fetch data from Bitstamp
        # data = self.fetch_bitstamp_data()
        # print(f"Collected: {data}")
        # self.save_to_mt5_format(data)

        return mt5_data

