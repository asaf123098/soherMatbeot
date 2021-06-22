import re
import os
import pandas as pd
from datetime import datetime, timedelta
from tqdm import tqdm

ONE_MINUTE = 60
ONE_HOUR = ONE_MINUTE * 60
ONE_DAY = ONE_HOUR * 24

REGEX = "(\d{,2})([a-zA-Z])"
INTERVAL_OPTS = [
    "8h",
    "6h",
    "4h",
    "2h",
    "15m",
    "12h",
    "30m",
    "5m",
    "3m",
    "1m",
    "1h",
    "1d"
]
N_CANDLES = 1000
START_DATETIME = datetime(2020, 1, 1)
DATA_PATH = "stocks_data"
OHLCV_COLUMN_NAMES = ["open_time", "open", "high", "low", "close", "volume"]


def _separate_amount_type(interval: str):
    interval_info = re.compile(REGEX).findall(interval)

    if not interval_info:
        raise ValueError("Something wrong with interval")

    n_interval, interval_type = interval_info[0]
    return int(n_interval), interval_type


def n_candles_to_start_date(start_date: datetime, interval):
    end_date = datetime.now()
    time_diff = end_date - start_date
    time_diff_in_seconds = time_diff.total_seconds()
    n_interval, interval_type = _separate_amount_type(interval)
    time_back = n_interval * N_CANDLES

    if interval_type == 'm':
        if time_diff_in_seconds / (ONE_MINUTE * n_interval) < N_CANDLES:
            time_back = (end_date - start_date).total_seconds() / (60 * n_interval)
        start_date = end_date - timedelta(minutes=time_back)
    elif interval_type == "h":
        if time_diff_in_seconds / (ONE_HOUR * n_interval) < N_CANDLES:
            time_back = (end_date - start_date).total_seconds() / (60 * 60 * n_interval)
        start_date = end_date - timedelta(hours=time_back)
    elif interval_type == "d":
        if time_diff_in_seconds / (ONE_DAY * n_interval) < N_CANDLES:
            time_back = (end_date - start_date).total_seconds() / (60 * 60 * 24 * n_interval)
        start_date = end_date - timedelta(days=time_back)
    elif interval_type == "w":
        if time_diff_in_seconds / (ONE_DAY * 7 * n_interval) < N_CANDLES:
            time_back = (end_date - start_date).total_seconds() / (60 * 60 * 24 * 7 * n_interval)
        start_date = end_date - timedelta(weeks=time_back)
    elif interval_type == "M":
        if time_diff_in_seconds / (ONE_DAY * 30 * n_interval) < N_CANDLES:
            time_back = (end_date - start_date).total_seconds() / (60 * 60 * 24 * 30 * n_interval)
        start_date = end_date - timedelta(days=time_back)
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
        folder_coin = os.path.join(DATA_PATH, coin)
        if os.path.exists(folder_coin):
            os.remove(folder_coin)

        os.mkdir(folder_coin)

        for interval in INTERVAL_OPTS:
            try:
                start_date_timestamp = n_candles_to_start_date(START_DATETIME, interval)
                data = client.get_historical_klines(coin, interval, start_str=start_date_timestamp)
                data_df = pd.DataFrame(data, columns=OHLCV_COLUMN_NAMES)
                data_df = change_df(data_df)
                filename = folder_coin + f"\\{interval}.csv"
                data_df.to_pickle(filename)
            except Exception as e:
                print(coin, interval)
                continue


if __name__ == "__main__":
    main()
