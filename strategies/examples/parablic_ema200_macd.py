import math

import pandas as pd
import pandas_ta as ta
import backtrader as bt
from backtrader import feeds
from strategies.strategy_abs import StrategyAbs

RISK = 1.1


class ParabolicSAR_EMA200_MACD(StrategyAbs):
    @staticmethod
    def prepare_data(data: pd.DataFrame) -> pd.DataFrame:
        data_copy = data.copy()
        data_copy.ta.psar(append=True)
        data_copy.ta.ema(200, append=True)
        data_copy.ta.macd(append=True)
        return data_copy

    def buy_signal(self, data: feeds):
        return data.close[0] > data.psarl_002_02[0] and data.open[0] > data.psarl_002_02[0] and \
               data.close[0] > data.ema_200[0] and data.macdh_12_26_9[0] > 0

    def sell_signal(self, data: feeds):
        return data.close[0] < data.psars_002_02[0] and data.open[0] < data.psars_002_02[0] and \
               data.close[0] > data.ema_200[0] and data.macdh_12_26_9[0] < 0

    def next(self):
        n_buys, amount = self._get_buys_stats()

        for i, data in enumerate(self.datas):
            if i == n_buys:
                break

            data_name = data._name
            position = self.getpositionbyname(data_name)

            if position.size == 0:  # If no money invested
                price = data.close[0] * 1.015
                size = (amount / price)
                size = float(f"{size:.03f}")

                if self.buy_signal(data) and size != 0:
                    stopprice = data.psarl_002_02[0]
                    take_profit = price + ((price - stopprice) * RISK)

                    print (f"size: {size}")
                    print (f"Amount: {amount}")
                    print(f"BUy: {price}")
                    print(f"stop: {stopprice}")
                    print(f"tp: {take_profit}")
                    self.buy_bracket(
                        data,
                        size=size,
                        exectype=bt.Order.Limit,
                        stopprice=stopprice,
                        price=price,
                        limitprice=take_profit
                    )
                # elif self.sell_signal(data) and size != 0:
                #     stopprice = data.psars_002_02[0]
                #     take_profit = price + ((price - stopprice) * RISK)
                #
                #     self.sell_bracket(
                #         data,
                #         size=size,
                #         exectype=bt.Order.Market,
                #         stopprice=take_profit,
                #         price=price,
                #         limitprice=take_profit
                #     )
