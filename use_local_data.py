import os
from os.path import join

import pandas as pd


def use_local_data(interval, path):
    coins_data = []
    symbols = os.listdir(path)

    for symbol in symbols:
        file_name = join(path, symbol, f"{interval}.pkl")
        data = pd.read_pickle(file_name)
        data["time"] = pd.to_datetime(data.time)
        data.rename(columns={"time": "datetime"}, inplace=True)
        data.set_index("datetime", inplace=True)

        if len(data) < 500:
            continue

        coins_data.append((symbol, data))

    return coins_data
