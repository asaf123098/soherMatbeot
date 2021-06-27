import os
from datetime import datetime
from os.path import join, abspath, dirname, exists

import bs4 as bs
import requests
import yfinance
from tqdm import tqdm

from data_fetchers.coin_data_fetcher import _separate_amount_type

START = datetime(2019, 6, 1)
END = datetime(2021, 6, 7)
INTERVAL = "1d"

N_CANDLES = 1000

ONE_MINUTE = 60
ONE_HOUR = ONE_MINUTE * 60
ONE_DAY = ONE_HOUR * 24

INTERVAL_OPTS = ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"]

STOCKS_DATA_DIR = abspath(join(dirname(__file__), "..", "stocks_data"))

OHLCV_COLUMN_NAMES = ["open_time", "open", "high", "low", "close", "volume"]


# def change_df(data: DataFrame):
#     data.rename(columns={"open_time": "time"}, inplace=True)
#     data["close"] = data.close.astype(float)
#     # data["open"] = data.open.astype(float)
#     # data["low"] = data.low.astype(float)
#     # data["high"] = data.high.astype(float)
#     # data["volume"] = data.volume.astype(float)
#     # data["time"] = pd.to_datetime(data.time, unit="ms")
#     return data[["time", "close", "high", "low", "open", "volume"]]


def _get_all_sp500_symbols():
    resp = requests.get('http://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    soup = bs.BeautifulSoup(resp.text, 'lxml')
    table = soup.find('table', {'class': 'wikitable sortable'})
    tickers = []
    for row in table.findAll('tr')[1:]:
        ticker = row.findAll('td')[0].text
        tickers.append(ticker)
    tickers = [s.replace('\n', '') for s in tickers]
    return tickers


def _verify_start_end():
    """This method verifies that the delta of the start and end time is ok with y finance"""
    assert END > START, "The start time must be before the end time!!!"

    n_interval, interval_type = _separate_amount_type(INTERVAL)
    if interval_type == "m":
        if n_interval == 1:
            assert (END - START).days <= 7, f"Max time for {INTERVAL} interval is 7 days!!"
            assert (datetime.now() - START).days <= 30, f"Start time must be within the last 30 days!!!"


if __name__ == "__main__":
    _verify_start_end()

    tickers = _get_all_sp500_symbols()

    for ticker in tqdm(tickers):
        data = yfinance.Ticker(ticker).history(interval=INTERVAL, start=START, end=END)
        data.rename(columns={"open_time": "time"}, inplace=True)

        ticker_folder = abspath(join(STOCKS_DATA_DIR, ticker))
        if not exists(ticker_folder): os.makedirs(ticker_folder)

        filename = join(ticker_folder, f"{INTERVAL}.pkl")
        data.to_pickle(filename)
