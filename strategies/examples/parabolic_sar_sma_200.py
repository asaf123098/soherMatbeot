import pandas as pd
import pandas_ta as ta
import backtrader as bt
from backtrader import feeds
from strategies.strategy_abs import StrategyAbs

RISK = 5


class ParabolicSAR_SMA200(StrategyAbs):
    @staticmethod
    def prepare_data(data: pd.DataFrame) -> pd.DataFrame:
        data_copy = data.copy()
        data_copy.ta.psar(append=True)
        data_copy.ta.sma(200, append=True)
        return data_copy

    def buy_signal(self, data: feeds):
        if data.low[0] > data.psarl_002_02[0]:
            return True
        return False

    def sell_signal(self, data: feeds):
        if data.psars_002_02[0] > data.high[0]:
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

                if data.sma_200[0] < price:   # When sma_200 is below price only take longs
                    stopprice = data.psarl_002_02[0]
                    take_profit = price + ((price - stopprice) * RISK)

                    if self.buy_signal(data) and size != 0:
                        self.buy_bracket(
                            data,
                            size=size,
                            exectype=bt.Order.Market,
                            stopprice=stopprice,
                            price=price,
                            limitprice=take_profit
                        )
                # elif data.sma_200[0] > price:  # When sma_200 is above price only take shorts
                #     stopprice = data.psars_002_02[0]
                #     take_profit = price + ((price - stopprice) * RISK)
                #
                #
                #     if self.sell_signal(data) and size != 0:
                #         self.sell_bracket(
                #             data,
                #             size=size,
                #             stopprice=stopprice,
                #             price=price,
                #             limitprice=take_profit
                #         )



