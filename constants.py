from enum import Enum
from binance.client import Client


class SignalOpts(Enum):
    NOTHING = 0
    BUY = 1
    SELL = 2


REG_COIN_ASSET = "USDT"
N_CORES = 4
INTERVAL_OPTS = [
    Client.KLINE_INTERVAL_1DAY,
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
    Client.KLINE_INTERVAL_1HOUR
]

OHLCV_COLUMN_NAMES = ["open_time", "open", "high", "low", "close", "volume", "close_time", "quote_asset_volume",
                      "n_trades", "base_asset_volume", "quote_asset_volume", "ignore"]

COMMISSION = 0.001
START_AMOUNT = 1000
