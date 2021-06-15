import math
import pandas as pd
import pandas_ta as ta
import backtrader as bt
from backtrader import feeds
from strategies.strategy_abs import StrategyAbs

RISK = 1.5
ATR_STOP_LOSS = 2


class SuperTrendStochEma200(StrategyAbs):
    @staticmethod
    def prepare_data(data: pd.DataFrame) -> pd.DataFrame:
        data_copy = data.copy()
        data_copy.ta.ema(200, append=True)
        data_copy.ta.supertrend(append=True)
        data_copy.rename(columns={"SUPERTl_7_3.0": "supertl"}, inplace=True)
        data_copy.ta.stoch(append=True)
        # print(data_copy.columns)

        return data_copy

    def buy_signal(self, data: feeds):
        if data.close[0] > data.ema_200 and not math.isnan(data.supertl[0]) and \
                data.stochk_14_3_3[-1] < data.stochd_14_3_3[-1] and data.stochk_14_3_3[0] > data.stochd_14_3_3[0]:
            return True
        return False

    def next(self):
        n_buys, amount = self._get_buys_stats()

        for i, data in enumerate(self.datas):
            if i == n_buys:
                break

            data_name = data._name
            position = self.getpositionbyname(data_name)

            if position.size == 0:  # If no money invested
                price = data.close[0]
                size = amount / price
                stopprice = price * 0.98
                take_profit = price * 1.03

                if self.buy_signal(data) and size != 0:
                    self.buy_bracket(
                        data,
                        size=size,
                        exectype=bt.Order.Market,
                        stopprice=stopprice,
                        price=price,
                        limitprice=take_profit
                    )
