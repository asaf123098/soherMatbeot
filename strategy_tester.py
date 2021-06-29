import math
import json
import pandas as pd
import backtrader as bt
from backtrader import plot
from typing import List, Tuple, Type, Dict

from tqdm import tqdm

from constants import COMMISSION, START_AMOUNT
from strategies.strategy_abs import StrategyAbs
from feed_creator import PandasFeedCreator
from use_local_data import Asset


class MySizer(bt.Sizer):
    def _getsizing(self, comminfo, cash, data, isbuy):
        price = data.close[0] * 1.01

        if cash * self.strategy.p.max_percentage > self.strategy.p.min_amount:
            size = self.strategy.p.max_percentage * self.broker.cash
        elif cash > self.strategy.p.min_amount:
            size = self.strategy.p.min_amount
        else:
            size = 0

        return size / price


class StrategyTester(object):
    start_amount = START_AMOUNT
    commission = COMMISSION

    def __init__(self, strategy: Type[StrategyAbs], data: List[Asset], **kwargs):
        self.kwargs = kwargs
        self.strategy = strategy
        self.data = data
        self.trading_period = self._get_trading_period()
        self._init_cerebro()
        self._load_data()
        self._run()

    def _get_trading_period(self):
        tmp_data = self.data[0].data_frame
        first_day = tmp_data.iloc[0].name
        last_day = tmp_data.iloc[-1].name
        return last_day - first_day

    def _init_cerebro(self):
        self.cerebro = bt.Cerebro(stdstats=False)
        # self.cerebro.addsizer(MySizer)
        self.cerebro.addobserver(bt.observers.Value)
        self.cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="trade_analyzer")
        self.cerebro.broker.setcommission(commission=self.commission)
        self.cerebro.broker.setcash(self.start_amount)
        self.cerebro.addstrategy(self.strategy, **self.kwargs)

    def _load_data(self):
        for asset in tqdm(self.data):
            prepared_data = self.strategy.prepare_data(asset.data_frame)
            data_feed = PandasFeedCreator.to_pandas_feed(prepared_data)
            self.cerebro.adddata(data_feed, name=asset.symbol)

    def _run(self):
        self.runstrategy = self.cerebro.run()[0]
        self.trade_analyzer = self.runstrategy.analyzers.trade_analyzer.get_analysis()

    def get_analysis(self) -> Dict:
        analysis = {}
        trades_json = json.loads(json.dumps(self.trade_analyzer))
        analysis["trades"] = trades_json
        analysis["trading_period"] = str(self.trading_period)
        analysis["starting_amount"] = float(self.start_amount)
        analysis["total_amount"] = float(self.cerebro.broker.get_value())
        analysis["daily_increase_percentage"] = self._calc_daily_increase()
        analysis["n_coins"] = len(self.data)
        return analysis

    def _calc_daily_increase(self):
        total_increase_percentage = self.cerebro.broker.get_value() / self.start_amount
        total_amount_of_days = self.trading_period.days

        if total_amount_of_days == 0:
            return "Either amount of days is not 1, TOTAL PERCENTAGE: " \
                   + str(total_increase_percentage)

        daily_increase = ((abs(total_increase_percentage) ** (1 / total_amount_of_days)) - 1) * 100

        if total_increase_percentage < 0:
            daily_increase *= -1

        return daily_increase

    def save_plot(self, path: str):
        plotter = plot.Plot()
        figure = plotter.plot(self.runstrategy)[0]
        figure.savefig(path)
