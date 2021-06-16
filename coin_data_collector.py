import re
import os
import csv
import pandas as pd
from datetime import datetime, timedelta
from binance.client import Client
from tqdm import tqdm

REGEX = "(\d{,2})([a-zA-Z])"
API_KEY = "5G3Tdy6uqvM8pgOjfxL7FmHQBwTTD1qlyZW6l0V8WrIAXDxIv15fGAzcMm9fXQbs"
SECRET_KEY = "CXgttdOy7l4CEfPeUqVOyEZGJvxB2Z2EuX8RaYLFbOKZzGeWkBPgqiGKOmfQCSm7"
INTERVAL_OPTS = [
    Client.KLINE_INTERVAL_8HOUR,
    Client.KLINE_INTERVAL_6HOUR,
    Client.KLINE_INTERVAL_4HOUR,
    Client.KLINE_INTERVAL_2HOUR,
    Client.KLINE_INTERVAL_15MINUTE,
    Client.KLINE_INTERVAL_12HOUR,
    Client.KLINE_INTERVAL_30MINUTE,
    Client.KLINE_INTERVAL_5MINUTE,
    Client.KLINE_INTERVAL_3MINUTE,
    Client.KLINE_INTERVAL_1MINUTE,
    Client.KLINE_INTERVAL_1HOUR,
    Client.KLINE_INTERVAL_1DAY
]
N_CANDLES = 1000
DATA_PATH = "d:\\coins_data\\"
OHLCV_COLUMN_NAMES = ["open_time", "open", "high", "low", "close", "volume", "close_time", "quote_asset_volume",
                      "n_trades", "base_asset_volume", "quote_asset_volume", "ignore"]


def _separate_amount_type(interval: str):
    interval_info = re.compile(REGEX).findall(interval)

    if not interval_info:
        raise ValueError("Something wrong with interval")

    n_interval, interval_type = interval_info[0]
    return int(n_interval), interval_type


def n_candles_to_start_date(n_candles, interval):
    start_date = None
    end_date = datetime.now()
    n_interval, interval_type = _separate_amount_type(interval)
    time_back = n_interval * n_candles

    if interval_type == 'm':
        start_date = end_date - timedelta(minutes=time_back)
    elif interval_type == "h":
        start_date = end_date - timedelta(hours=time_back)
    elif interval_type == "d":
        start_date = end_date - timedelta(days=time_back)
    elif interval_type == "w":
        start_date = end_date - timedelta(weeks=time_back)
    elif interval_type == "M":
        start_date = end_date - timedelta(days=time_back * 30)
    else:
        ValueError("Wrong Interval")

    start_date_timestamp = int(start_date.timestamp() * 1000)
    return start_date_timestamp


def change_df(data):
    data.rename(columns={"close_time": "time"}, inplace=True)
    data["close"] = data.close.astype(float)
    data["open"] = data.open.astype(float)
    data["low"] = data.low.astype(float)
    data["high"] = data.high.astype(float)
    data["volume"] = data.volume.astype(float)
    data["time"] = pd.to_datetime(data.time, unit="ms")
    return data[["time", "close", "high", "low", "open", "volume"]]


def main():
    client = Client(API_KEY, SECRET_KEY)
    coins_list = client.get_all_tickers()
    coins_usdt_list = [row["symbol"] for row in coins_list if row["symbol"].endswith("USDT")]

    for coin in tqdm(coins_usdt_list):
        folder_coin = DATA_PATH + coin
        if os.path.exists(folder_coin):
            os.remove(folder_coin)

        os.mkdir(folder_coin)

        for interval in INTERVAL_OPTS:
            start_date_timestamp = n_candles_to_start_date(N_CANDLES, interval)
            data = client.get_historical_klines(coin, interval, start_str=start_date_timestamp)
            data_df = pd.DataFrame(data, columns=OHLCV_COLUMN_NAMES)
            data_df = change_df(data_df)
            filename = folder_coin + f"\\{interval}.csv"
            data_df.to_csv(filename, index=False)


if __name__ == "__main__":
    main()
