"""dataProvider.py contains getting data from differen data providers and 
converting them to the MT5 format.

"""

import yfinance as yf
import investpy
import requests
import pandas as pd
from datetime import datetime, timezone, timedelta
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
    

class DataProvider(MT5_funcs):
    def __init__(self):
        super().__init__()
        
        self.directory = "../../Files/CSV_data/"
        # Bybit API Endpoint for K-line data
        self.bybit_url = "https://api.bybit.com/v2/public/kline/list"
        # Bitstamp API URL for BTC/USD ticker
        self.bitstamp_url = "https://www.bitstamp.net/api/v2/ticker/btcusd/"

        self.last_date = "2024-12-28"

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
        
        

        # print(data.head())
        data.reset_index(inplace=True)
        data = data.rename(columns={
            "Datetime": "Time", 
            "Open": "Open", 
            "High": "High", 
            "Low": "Low", 
            "Close": "Close", 
            "Volume": "Volume"
        })
        
        # Format data for MT5 (Time, Open, High, Low, Close, Volume)
        data = data[["Time", "Open", "High", "Low", "Close", "Volume"]]
        # Convert the 'Datetime' column to the required format
        data['Time'] = pd.to_datetime(data['Time']).dt.strftime('%Y.%m.%d %H:%M')
        # print(data.head())
        # Flatten multi-index columns
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = [f"{col[0]}" for col in data.columns]
        # print(data.head())
        return data

    def save_to_existing_csv(self, data, filename="BTCUSD_m1.csv"):
        """
        Save the MT5-compatible data to an existing CSV file.
        """
        # open the existing file and append the new data
        existing_data = pd.read_csv(f"{self.directory}{filename}")
        existing_data = pd.concat([existing_data, data], ignore_index=True)
        # remove duplicates
        existing_data.drop_duplicates(subset=["Time"], keep="last", inplace=True)
        existing_data.to_csv(f"{self.directory}{filename}", index=False, sep=',')
        # print(f"Data saved to {filename}")

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
        # Important: Use either start/end or period, not both.
        if start is None:
            data = yf.download(tickers=symbol, period=period, interval=interval, progress=False)
        else:
            data = yf.download(tickers=symbol, start=start, end=end, interval=interval, progress=False)

        if not data.empty:
            self.last_date = data.index[-1].to_pydatetime() + timedelta(days=1)
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

    def fetch_data(self, source = "yfinance", symbol="NVDA", start=None, end=None, period="1d", interval="1m", limit=200):
        """
        Fetch data from different providers and prepare for MT5.
        """
        if source == "yfinance":
            data = self.fetch_yfinance_data(symbol, start, end, period, interval)
            mt5_data = self.prepare_mt5_format(data)
            self.save_to_existing_csv(mt5_data, f"{symbol}_{interval}.csv")
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

        return self.last_date.strftime('%Y-%m-%d'), True

    def fetch_data_in_chunks(self, source = "yfinance", symbol="NVDA", start="New", interval="1m", chunk_days=7):
        all_data = []
        finish = False

        # data = yf.download(tickers=symbol, period="1d", interval=interval, progress=False)
        data = self.fetch_yfinance_data(symbol, period="1d", interval=interval)
        # Check if data is available
        if data.empty:
            print(f"No data available for symbol: {symbol}")
            return None
        # Get the last available date
        current_end = self.last_date
        # print(f"Last available date for {symbol}: {current_end.strftime('%Y-%m-%d')}")
        if start != "New":
            start_date = datetime.strptime(start, '%Y-%m-%d').replace(tzinfo=timezone.utc) + timedelta(hours=23, minutes=59)
            # if the start date is greater than the last available date, return
            if start_date >= current_end:
                return self.last_date.strftime('%Y-%m-%d'), False

        while True:
            chunk_start = current_end - timedelta(days=chunk_days)
            if start != "New" and chunk_start < start_date:
                chunk_start = start_date
                finish = True
            # print(f"Fetching data from {chunk_start}")

            # get data for the chunk
            if source == "yfinance":
                data = self.fetch_yfinance_data(symbol=symbol, start=chunk_start.strftime('%Y-%m-%d'), end=current_end.strftime('%Y-%m-%d'), interval=interval)
            
            if data.empty:
                while data.empty and chunk_start < current_end:
                    chunk_start = chunk_start + timedelta(days=1)
                    data = self.fetch_yfinance_data(symbol=symbol, start=chunk_start.strftime('%Y-%m-%d'), end=current_end.strftime('%Y-%m-%d'), interval=interval)
                # print("No more data available.")
                all_data.insert(0, data)
                break
            # Append the chunk to the beginning of the list
            all_data.insert(0, data)
            # all_data.append(data)
            if finish:
                break
            # Move to the next chunk
            current_end = chunk_start

        # Concatenate all chunks into a single DataFrame
        if all_data:
            all_data = pd.concat(all_data)
            mt5_data = self.prepare_mt5_format(all_data)
            # Save the data to a CSV file for first time
            if start == "New":
                mt5_data.to_csv(f"{self.directory}{symbol}_{interval}.csv", index=False, sep=',')
            else:
                self.save_to_existing_csv(mt5_data, f"{symbol}_{interval}.csv")

        return self.last_date.strftime('%Y-%m-%d'), True
    
    