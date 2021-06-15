import pandas as pd
import pandas_ta as ta
import backtrader as bt
from backtrader import feeds
from strategies.strategy_abs import StrategyAbs


RISK = 1.5
ATR_STOP_LOSS = 2


def STC(ohlc: pd.DataFrame, period_fast: int = 23, period_slow: int = 50, k_period: int = 10, d_period: int = 3,
        column: str = "close", adjust: bool = True) -> pd.Series:
    EMA_fast = pd.Series(
        ohlc[column].ewm(ignore_na=False, span=period_fast, adjust=adjust).mean(),
        name="EMA_fast",
    )

    EMA_slow = pd.Series(
        ohlc[column].ewm(ignore_na=False, span=period_slow, adjust=adjust).mean(),
        name="EMA_slow",
    )

    MACD = pd.Series((EMA_fast - EMA_slow), name="MACD")

    STOK = pd.Series((
                             (MACD - MACD.rolling(window=k_period).min())
                             / (MACD.rolling(window=k_period).max() - MACD.rolling(window=k_period).min())
                     ) * 100)

    STOD = STOK.rolling(window=d_period).mean()
    STOD_DoubleSmooth = STOD.rolling(window=d_period).mean()  # "double smoothed"
    return pd.Series(STOD_DoubleSmooth, name="stc_{0}".format(k_period))


class IchiStcCmf(StrategyAbs):
    @staticmethod
    def prepare_data(data: pd.DataFrame) -> pd.DataFrame:
        data_copy = data.copy()
        data_copy.ta.ichimoku(append=True)
        data_copy["stc"] = STC(data_copy)
        data_copy.ta.cmf(append=True)
        data_copy.ta.atr(append=True)

        return data_copy

    def buy_signal(self, data: feeds):
        if data.isa_9[0] < data.close[0] and data.isb_26[0] < data.close[0] and data.cmf_20[0] > 0 and data.stc > 75:
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
                stopprice = price - data.atrr_14[0] * ATR_STOP_LOSS
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
