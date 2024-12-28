import pandas as pd
import time
import dataProvider
from inputimeout import inputimeout


# Note: add new symbols to the list in "symbols.csv" file
# for new symbols, set "last_date" to "New"
# symbols = [
#     {"symbol": "NVDA", "source": "yfinance", "last_date": "0"},
#     {"symbol": "ASML.AS", "source": "yfinance", "last_date": "0"},
#     {"symbol": "TSLA", "source": "yfinance", "last_date": "0"}
# ]


def save_to_mt5_format(data):
    with open(mt5_file, 'a') as f:
        f.write(f"{data['date']},{data['time']},{data['open']},{data['high']},{data['low']},{data['close']},{data['volume']}\n")


if __name__ == "__main__":
    
    # read symbols from CSV file
    df_symbols = pd.read_csv('symbols.csv')
    symbols = df_symbols.to_dict(orient='records')
    # print(symbols)
    
    data = dataProvider.DataProvider()
    # # connect to MetaTrader 5
    # if not data.connect_to_mt5():
    #     data.disconnect_from_mt5()
    # else:
    if True:

        for symbol in symbols:
            current_date, exist_data = data.fetch_data_in_chunks(source=symbol["source"], symbol=symbol["symbol"], start=symbol["last_date"], interval="1m", chunk_days=7)
            if exist_data:
                symbol["last_date"] = current_date
        while True:
            for symbol in symbols:
                current_date, exist_data = data.fetch_data(source=symbol["source"], symbol=symbol["symbol"], period="1d", interval="1m")
                if exist_data:
                    symbol["last_date"] = current_date
            try:
                time_over = inputimeout(prompt='End (y/n): ', timeout=5)
                if time_over == "y":
                    break
                else:
                    time.sleep(5)  # wait x seconds
                    print('\033[A', end="")
            except Exception:
                print('\033[A', end="")

    # convert symbols to panda and save it to CSV file
    df_symbols = pd.DataFrame(symbols)
    df_symbols.to_csv('symbols.csv', index=False, columns=["symbol", "source", "last_date"])

    # data.disconnect_from_mt5()


    