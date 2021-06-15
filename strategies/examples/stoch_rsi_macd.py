import pandas as pd
import pandas_ta as ta
import backtrader as bt
from backtrader import feeds
from strategies.strategy_abs import StrategyAbs

RISK = 1.5
N_CANDLES_BACK = 10


class StochRsiMACD(StrategyAbs):
    @staticmethod
    def prepare_data(data: pd.DataFrame) -> pd.DataFrame:
        data_copy = data.copy()
        data_copy.ta.macd(append=True)
        data_copy.ta.stoch(append=True)
        data_copy.ta.rsi(append=True)
        return data_copy

    def buy_signal(self, data: feeds):
        stoch_reached_oversold = False
        stoch_reached_overbought = False
        rsi_crossed_middle_line = False
        positive_historgram = False

        for i in range(-1 * N_CANDLES_BACK, 1):
            if data.stochk_14_3_3[i] < 20 and data.stochd_14_3_3[i] < 20:
                stoch_reached_oversold = True
            if data.stochk_14_3_3[i] > 80 and data.stochd_14_3_3[i] > 80:
                stoch_reached_overbought = True

        if data.macdh_12_26_9[0] > 0:
            positive_historgram = True

        if data.rsi_14[0] > 50:
            rsi_crossed_middle_line = True

        return positive_historgram and rsi_crossed_middle_line and stoch_reached_oversold \
               and not stoch_reached_overbought

    def _get_stop_loss(self, data):
        min_value = None

        for i in range(-1 * N_CANDLES_BACK, 1):
            price = data.close[i]

            if not min_value:
                min_value = price
            elif price < min_value:
                min_value = price

        return min_value

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
                stoploss = self._get_stop_loss(data)
                take_profit = price + (price - stoploss) * RISK

                if self.buy_signal(data):
                    self.buy_bracket(
                        data=data,
                        size=size,
                        exectype=bt.Order.Market,
                        stopprice=stoploss,
                        price=price,
                        limitprice=take_profit
                    )
