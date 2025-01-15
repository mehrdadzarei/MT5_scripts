import pandas as pd
import time
import dataProvider
from inputimeout import inputimeout
import shutil


# Note: add new symbols to the list in "symbols.csv" file
# for new symbols, set "last_date" to "New"
# symbols = [
#     {"symbol": "NVDA", "source": "yfinance", "last_date": "0"},
#     {"symbol": "ASML.AS", "source": "yfinance", "last_date": "0"},
#     {"symbol": "TSLA", "source": "yfinance", "last_date": "0"}
# ]

source_path = "C:\\Users\\mzarei\\AppData\\Roaming\\MetaQuotes\\Terminal\\D0E8209F77C8CF37AD8BF550E51FF075\\MQL5\\Scripts\\MT5_scripts\\symbols.csv"
dest_path = "C:\\Users\\mzarei\\AppData\\Roaming\\MetaQuotes\\Terminal\\D0E8209F77C8CF37AD8BF550E51FF075\\MQL5\\Files\\symbols.csv"



def copy_file(source, dest):
    shutil.copy(source, dest)

if __name__ == "__main__":
    
    copy_file(source_path, dest_path)
    # read symbols from CSV file
    df_symbols = pd.read_csv(source_path)
    symbols = df_symbols.to_dict(orient='records')
    # print(symbols)
    
    data = dataProvider.DataProvider()
    # # connect to MetaTrader 5
    # if not data.connect_to_mt5():
    #     data.disconnect_from_mt5()
    # else:
    if True:

        for symbol in symbols:
            # data.fetch_data(source=symbol["source"], symbol=symbol["sr_symbol"], period="1d", interval="1m")
            # data.fetch_bitstamp_data()
            for interval in ["1m", "5m", "1h", "1d"]:
                data.fetch_all_data(source=symbol["source"], symbol=symbol["sr_symbol"], interval=interval)
            print(f"Data for symbol {symbol['sr_symbol']} is fetched successfully.")
        while True:
            for symbol in symbols:
                for interval in ["1m", "5m", "1h", "1d"]:
                    data.fetch_data(source=symbol["source"], symbol=symbol["sr_symbol"], period="1d", interval=interval)
                print(f"Data for symbol {symbol['sr_symbol']} is fetched successfully.")
            # try:
            time_over = inputimeout(prompt='End (y/n): ', timeout=5)
            if time_over == "y":
                break
            else:
                time.sleep(30)  # wait x seconds
                # print('\033[A', end="")
            # except Exception:
            #     print('\033[A', end="")

    # convert symbols to panda and save it to CSV file
    df_symbols = pd.DataFrame(symbols)
    df_symbols.to_csv(source_path, index=False, columns=["mt5_symbol", "sr_symbol", "source"])

    copy_file(source_path, dest_path)
    
    # data.disconnect_from_mt5()


