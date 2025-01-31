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
        
        self.directory = "C:/Users/mzarei/AppData/Roaming/MetaQuotes/Terminal/D0E8209F77C8CF37AD8BF550E51FF075/MQL5/Files/"
        # Bybit API Endpoint for K-line data
        self.bybit_url = "https://api.bybit.com/v2/public/kline/list"
        # Bitstamp API URL for BTC/USD ticker
        self.bitstamp_url = f"https://www.bitstamp.net/api/v2/ohlc/" # {pair}/"
        # Fetch OHLC data from CoinGecko API.
        self.coinGecko_url = f"https://api.coingecko.com/api/v3/coins/" #{coin_id}/ohlc"
        self.binance_url = "https://api.binance.com/api/v3/klines"

        self.last_date = "2024-12-28"
        # Define max chunk_days for each interval
        self.chunk_days_limits = {
            "1m": 7,
            "2m": 60,
            "5m": 60,
            "15m": 60,
            "30m": 60,
            "1h": 730,
            "1d": 10000,  # No real limit for daily data
            "1wk": 10000, # No real limit for weekly data
            "1mo": 10000  # No real limit for monthly data
        }

    def prepare_mt5_format(self, data):
        """
        Prepare the data in MT5-compatible format.
        """
        # print(data.head())
        # Flatten multi-index columns
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = [f"{col[0]}" for col in data.columns]
        # print(data.head())
        data.reset_index(inplace=True)
        data = data.rename(columns={
            "timestamp": "Time", 
            "Datetime": "Time", 
            "Date": "Time", 
            "open": "Open", 
            "high": "High", 
            "low": "Low", 
            "close": "Close", 
            "volume": "Volume"
        })
        # print(data.head())
        
        # Check if the first column contains datetime values
        # if pd.to_datetime(data.index, errors='coerce').notna().all():
        #     data.index.name = 'Time'
        #     data.reset_index(inplace=True)
        # print(data.head())

        # Remove any columns that are not in the required format
        required_columns = ["Time", "Open", "High", "Low", "Close", "Volume"]
        data = data[required_columns]
        # data.reset_index(inplace=True)
        # print(data.head())
        # Convert the 'Datetime' column to the required format
        data['Time'] = pd.to_datetime(data['Time']).dt.strftime('%Y.%m.%d %H:%M')
        # print(data.head())
        return data

    def save_to_csv(self, data, filename="BTC-USD_m1.csv"):
        """
        Save the MT5-compatible data to a CSV file.
        """
        # open or create the file and append the new data
        while True:
            try:
                existing_data = pd.read_csv(f"{self.directory}{filename}")
                existing_data = pd.concat([existing_data, data], ignore_index=True)
                # remove duplicates
                existing_data.drop_duplicates(subset=["Time"], keep="last", inplace=True)
                existing_data.to_csv(f"{self.directory}{filename}", index=False, sep=',')
                break
            except PermissionError:
                # print(f"File {filename} is currently open by another program. Waiting for it to be closed...")
                time.sleep(10)
            except FileNotFoundError:
                data.to_csv(f"{self.directory}{filename}", index=False, sep=',')
                break
        
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
    
    def get_valid_start_date(self, days):
        # Calculate days back from today
        today = datetime.now()
        valid_start_date = today - timedelta(days=days - 1)
        return valid_start_date.replace(tzinfo=timezone.utc)
    
    def fetch_yfinance_data(self, symbol="ASML", start=None, end=None, period="max", interval="1m"):
        """
        Fetch historical data from Yahoo Finance using yfinance.
        """
        # Important: Use either start/end or period, not both.
        try:
            if start is None:
                data = yf.download(tickers=symbol, period=period, interval=interval, progress=False)
            else:
                data = yf.download(tickers=symbol, start=start, end=end, interval=interval, progress=False)
        except Exception as e:
            print(f"Error fetching data: {e}")
            return None

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

    def fetch_bitstamp_data(self, symbol="btcusd", interval="1m", start=None, end=None, limit=1000):
        if interval == "1m":
            step = 60
        elif interval == "5m":
            step = 300
        elif interval == "1h":
            step = 3600
        elif interval == "1d":
            step = 86400
        
        params = {
            "step": step,   # Interval in seconds (60 = 1 minute)
            "limit": limit  # 1000 Maximum per request
        }
        if start:
            params["start"] = start
        if end:
            params["end"] = end
        
        url = f"{self.bitstamp_url}{symbol}/"
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            ohlc = data["data"]["ohlc"]
            df = pd.DataFrame(ohlc, index=None)
            df["timestamp"] = pd.to_datetime(df["timestamp"].astype(int), unit="s")
            # print(df.head())
            # print(df.tail())
            # if there is data, update the last date
            if not df.empty:
                self.last_date = df["timestamp"].iloc[-1].to_pydatetime()
            return df
        else:
            print(f"Error {response.status_code}: {response.text}")
            return None
    
    def fetch_investpy_data(self, symbol="BTC/USD", start="01/01/2021", end="31/01/2021"):
        """
        Fetch historical data from Investing.com using investpy
        """

    def fetch_coingecko_data(self, symbol="bitcoin", days=1):
        """
        Fetch historical OHLC data from CoinGecko API.
        """
        params = {
            "vs_currency": "usd",
            "days": days
        }
        
        url = f"{self.coinGecko_url}{symbol}/ohlc"
        response = requests.get(url, params=params)

        if response.status_code == 200:
            data = response.json()
            # Create DataFrame with appropriate column names
            df = pd.DataFrame(data, columns=["timestamp", "Open", "High", "Low", "Close"])
            # Convert timestamp to datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            print(df.head())
            print(df.tail())
            return df
        else:
            print(f"Error {response.status_code}: {response.text}")
            return None

    def fetch_binance_data(self, symbol="BTCUSDT", interval="1m", start=None, end=None, limit=1000):
        """
        Fetch historical data from Binance API.
        """
        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": limit
        }
        if start:
            params["startTime"] = start
        if end:
            params["endTime"] = end
        
        response = requests.get(self.binance_url, params=params)
        if response.status_code == 200:
            
            data = response.json()
            # Create DataFrame with appropriate column names
            df = pd.DataFrame(data, columns=["timestamp", "Open", "High", "Low", "Close", "Volume", "CloseTime", "QuoteAssetVolume", "NumberOfTrades", "TakerBuyBaseAssetVolume", "TakerBuyQuoteAssetVolume", "Ignore"])
            # Convert timestamp to datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            print(df.head())
            print(df.tail())

    def fetch_data(self, source = "yfinance", symbol="NVDA", start=None, end=None, period="1d", interval="1m", limit=200):
        """
        Fetch data from different providers and prepare for MT5.
        """
        if source == "yfinance":
            data = self.fetch_yfinance_data(symbol, start, end, period, interval)
        elif source == "bybit":
            kline_data = self.fetch_bybit_kline(symbol, interval, limit)
        elif source == "bitstamp":
            data = self.fetch_bitstamp_data(symbol, interval, start, end)
        else:
            raise ValueError("Invalid source specified.")
        

        # # Fetch data from Bitstamp
        # data = self.fetch_bitstamp_data()
        # print(f"Collected: {data}")
        # self.save_to_mt5_format(data)

        if data is not None:
            mt5_data = self.prepare_mt5_format(data)
            self.save_to_csv(mt5_data, f"{symbol}_{interval}.csv")
        
        # return self.last_date.strftime('%Y-%m-%d'), True

    def fetch_yfinance_data_in_chunks(self, source = "yfinance", symbol="NVDA", interval="1m"):
        all_data = []
        finish = False

        chunk_days = self.chunk_days_limits.get(interval, 7)
        if interval == "1m":
            limit = 30  # 30 days of 1-minute data
        else:
            limit = chunk_days
        valid_start_date = self.get_valid_start_date(days=limit)

        data = self.fetch_yfinance_data(symbol, period="1d", interval=interval)
        # Check if data is available
        if data.empty:
            print(f"No data available for symbol: {symbol}")
            return None
        # Get the last available date
        current_end = self.last_date
        # open the existing file if exists then get the last date from last row
        try:
            existing_data = pd.read_csv(f"{self.directory}{symbol}_{interval}.csv")
            start_date = existing_data["Time"].iloc[-1]
            start_date = datetime.strptime(start_date, '%Y.%m.%d %H:%M').replace(tzinfo=timezone.utc)
        except FileNotFoundError:
            pass

        while True:
            chunk_start = current_end - timedelta(days=chunk_days)
            if 'start_date' in locals() and chunk_start.replace(tzinfo=timezone.utc) < start_date:
                chunk_start = start_date
                finish = True
            # print(f"Fetching data from {chunk_start}")
            if chunk_start.replace(tzinfo=timezone.utc) <= valid_start_date:
                chunk_start = valid_start_date
                finish = True

            # get data for the chunk
            if source == "yfinance":
                if 'start_date' in locals() or interval == "1m":
                    data = self.fetch_yfinance_data(symbol=symbol, start=chunk_start.strftime('%Y-%m-%d'), end=current_end.strftime('%Y-%m-%d'), interval=interval)
                else:
                    data = self.fetch_yfinance_data(symbol=symbol, period="max", interval=interval)
                    finish = True
                
            if data.empty:
                while data.empty and chunk_start < current_end:
                    chunk_start = chunk_start + timedelta(days=1)
                    data = self.fetch_yfinance_data(symbol=symbol, start=chunk_start.strftime('%Y-%m-%d'), end=current_end.strftime('%Y-%m-%d'), interval=interval)
                # print("No more data available.")
                all_data.insert(0, data)
                break
            # Append the chunk to the beginning of the list
            all_data.insert(0, data)
            if finish:
                break
            # Move to the next chunk
            current_end = chunk_start

        # Concatenate all chunks into a single DataFrame
        if all_data:
            all_data = pd.concat(all_data)
            mt5_data = self.prepare_mt5_format(all_data)
            self.save_to_csv(mt5_data, f"{symbol}_{interval}.csv")

        # return self.last_date.strftime('%Y-%m-%d'), True
    
    def fetch_bitstamp_data_in_chunks(self, source = "bitstamp", symbol="btcusd", interval="1m"):
        """
        Fetch all available OHLC data from Bitstamp for a specific interval.
        """
        all_data = []
        data = self.fetch_bitstamp_data(symbol, interval=interval, limit=10)
        # Check if data is available
        if data.empty:
            print(f"No data available for symbol: {symbol}")
            return None
        # Get the last available date
        current_end = int(self.last_date.timestamp())

        # open the existing file if exists then get the last date from last row
        try:
            existing_data = pd.read_csv(f"{self.directory}{symbol}_{interval}.csv")
            start_date = existing_data["Time"].iloc[-1]
            start_date = datetime.strptime(start_date, '%Y.%m.%d %H:%M').replace(tzinfo=timezone.utc)
        except FileNotFoundError:
            pass

        while True:
            df = self.fetch_bitstamp_data(symbol, interval, end=current_end)
            if df is None or df.empty:
                break
            all_data.insert(0, df)
            # Update current_end to the earliest timestamp in the current batch
            current_end = int(df["timestamp"].iloc[0].timestamp())
            print(f"Fetched {len(df)} rows. Earliest timestamp: {df['timestamp'].iloc[-1]}")
            # Break loop if fewer rows are fetched (no more historical data)
            if len(df) < 1000:
                break
            if 'start_date' in locals() and datetime.fromtimestamp(current_end, tz=timezone.utc) < start_date:
                break
            # if current_end < int(datetime(2023, 1, 1).timestamp()):
            #     break
            time.sleep(1)  # Prevent hitting API rate limits

        # Concatenate all chunks into a single DataFrame
        if all_data:
            all_data = pd.concat(all_data)
            mt5_data = self.prepare_mt5_format(all_data)
            self.save_to_csv(mt5_data, f"{symbol}_{interval}.csv")

        # return self.last_date.strftime('%Y-%m-%d'), True

    def fetch_all_data(self, source = "yfinance", symbol="NVDA", interval="1m"):
        """
        Fetch all available data for the specified symbol and interval.
        """
        if source == "yfinance":
            self.fetch_yfinance_data_in_chunks(source, symbol, interval)
        elif source == "bitstamp":
            self.fetch_bitstamp_data_in_chunks(source, symbol, interval)
        else:
            raise ValueError("Invalid source specified.")
    