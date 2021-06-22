import os

import pandas as pd


def use_local_data(interval, path):
    coins_data = []
    coin_names = os.listdir(path)

    for coin in coin_names:
        file_name = path + f"\\{coin}\\{interval}.csv"
        data = pd.read_csv(file_name)
        data["time"] = pd.to_datetime(data.time)
        data.rename(columns={"time": "datetime"}, inplace=True)
        data.set_index("datetime", inplace=True)

        if len(data) < 500:
            continue

        coins_data.append((coin, data))

    return coins_data
