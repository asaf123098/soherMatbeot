import pandas as pd
import backtrader as bt
from backtrader import feeds
from strategies.strategy_abs import StrategyAbs

RISK = 1.1
TRADE_PRICE_OFFSET = 0.02


def _get_buy_price(close_price: int):
    return close_price + (close_price * TRADE_PRICE_OFFSET)


def _get_short_price(close_price: int):
    return close_price - (close_price * TRADE_PRICE_OFFSET)


class Sizer(bt.Sizer):
    def _getsizing(self, comminfo, cash, data, isbuy):
        if isbuy:
            price = _get_buy_price(data.close[0])

            if price > cash:
                size = 0
            else:
                size = (cash * self.strategy.p.max_percentage) // price

            return size


class BracketOrder:

    def __init__(self, buy_order, sell_order):
        self.buy_order = buy_order
        self.sell_order = sell_order


class EMA200_50_20(StrategyAbs):
    params = (
        ("max_percentage", 0.2),
        ("interval", 20),
    )

    def __init__(self):
        super(EMA200_50_20, self).__init__()
        self.sizer = Sizer

    @staticmethod
    def prepare_data(data: pd.DataFrame) -> pd.DataFrame:
        data_copy = data.copy()
        data_copy.ta.ema(200, append=True)
        data_copy.ta.ema(50, append=True)
        data_copy.ta.ema(8, append=True)
        return data_copy

    def buy_signal(self, data: feeds):
        return data.close[0] > data.ema_200[0] and data.close[0] > data.ema_50[0] and \
               data.open[0] < data.ema_8[0] and data.close[0] > data.ema_8[0]

    def sell_signal(self, data: feeds):
        return data.close[0] < data.ema_200[0] and data.close[0] < data.ema_50[0] and \
               data.open[0] > data.ema_8[0] and data.close[0] < data.ema_8[0]

    def next(self):
        for asset in self.datas:

            data_name = asset._name
            position = self.getpositionbyname(data_name)

            if position.size == 0:  # If no money invested in the asset

                if self.buy_signal(asset):
                    price = self.__get_trade_price(asset.close[0])

                    stopprice = asset.psarl_002_02[0]
                    take_profit = price + ((price - stopprice) * RISK)

                    print(f"size: {size}")
                    print(f"Amount: {amount}")
                    print(f"BUy: {price}")
                    print(f"stop: {stopprice}")
                    print(f"tp: {take_profit}")
                    self.buy(
                        asset,
                        exectype=bt.Order.Limit,
                        price=price,
                    )
                elif self.sell_signal(asset):
                    stopprice = data.psars_002_02[0]
                    take_profit = price + ((price - stopprice) * RISK)

                    self.sell_bracket(
                        data,
                        exectype=bt.Order.Market,
                        price=price,
                    )
