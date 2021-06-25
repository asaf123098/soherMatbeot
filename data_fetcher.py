import os
import pandas as pd


DATA_FOLDER = "coins_data"


def fetch_data(interval):
    coins_data = []
    coin_names = os.listdir(DATA_FOLDER)

    for coin in coin_names:
        file_name = DATA_FOLDER + f"\\{coin}\\{interval}.pklz"
        data = pd.read_pickle(file_name)
        data["time"] = pd.to_datetime(data.time)
        data.rename(columns={"time": "datetime"}, inplace=True)
        data.set_index("datetime", inplace=True)

        if len(data) < 500:
            continue

        coins_data.append((coin, data))

    return coins_data