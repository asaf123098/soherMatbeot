import os
from os.path import join

import pandas as pd


class Asset:

    def __init__(self, symbol: str, data: pd.DataFrame):
        self.symbol = symbol
        self.data_frame = data


def use_local_data(interval, path):
    coins_data = []
    symbols = os.listdir(path)

    for symbol in symbols:
        file_name = join(path, symbol, f"{interval}.pkl")
        data = pd.read_pickle(file_name)
        data["time"] = pd.to_datetime(data.time)
        data.rename(columns={"time": "datetime"}, inplace=True)
        data.set_index("datetime", inplace=True)

        if is_data_length_valid(data):
            coins_data.append(Asset(symbol, data))

    return coins_data


def use_local_stocks_data(interval, path):
    assets = []
    symbols = os.listdir(path)

    for symbol in symbols:
        file_name = join(path, symbol, f"{interval}.pkl")
        asset_data = pd.read_pickle(file_name)
        if is_data_length_valid(asset_data):
            assets.append(Asset(symbol, asset_data))

        # TODO: Remove
        if len(assets) > 2:
            break

    return assets


def is_data_length_valid(data: pd.DataFrame):
    return len(data) > 500
