import os
import glob
import pandas as pd


DATA_FOLDER = "coins_data"


def fetch_data(interval):
    coins_data = []
    coins_data_files = glob.glob(DATA_FOLDER + f"\\*\\{interval}.pklz")

    for coin_file in coins_data_files:
        coin = coin_file.split("\\")[1]
        data = pd.read_pickle(coin_file)
        data["time"] = pd.to_datetime(data.time)
        data.rename(columns={"time": "datetime"}, inplace=True)
        data.set_index("datetime", inplace=True)

        if len(data) < 500:
            continue

        coins_data.append((coin, data))

    return coins_data