import pandas as pd
import pandas_ta as ta
import backtrader as bt
from backtrader import feeds
from strategies.strategy_abs import StrategyAbs

RISK = 1.5
ATR_STOP_LOSS = 2


class ThreeEmaStochRsi(StrategyAbs):
    @staticmethod
    def prepare_data(data: pd.DataFrame) -> pd.DataFrame:
        data_copy = data.copy()
        data_copy.ta.ema(50, append=True)
        data_copy.ta.ema(14, append=True)
        data_copy.ta.ema(8, append=True)
        data_copy.ta.stochrsi(append=True)
        data_copy.ta.atr(append=True)

        return data_copy

    def buy_signal(self, data: feeds):
        if data.close[0] > data.ema_8[0] > data.ema_14[0] > data.ema_50[0] and \
                data.stochrsik_14_14_3_3[0] > data.stochrsid_14_14_3_3[0]:
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
                stopprice = price - data.atrr_14[0] * 3
                take_profit = price + data.atrr_14[0] * 2

                if self.buy_signal(data) and size != 0:
                    self.buy_bracket(
                        data,
                        size=size,
                        exectype=bt.Order.Market,
                        stopprice=stopprice,
                        price=price,
                        limitprice=take_profit
                    )
