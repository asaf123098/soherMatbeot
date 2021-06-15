import math
from typing import List

import pandas as pd
import backtrader as bt
from backtrader import Strategy, Order
from abc import abstractmethod


class StrategyAbs(Strategy):
    params = (
        ("max_percentage", 0.8),
        ("min_amount", 20),
    )

    def __init__(self):
        self.orders = {data._name: None for data in self.datas}

    def notify_order(self, order):
        data_name = order.data._name
        order_type = "BUY" if order.isbuy() else "SELL"

        if order.status in [order.Accepted or order.Submitted]:
            return
        # elif order.status in [order.Completed]:
        #     print(f"{data_name}: {order_type} Order Completed, Price: {order.executed.price}")
        # elif order.status in [order.Canceled, order.Margin, order.Rejected]:
        #     print(f'{data_name}: {order_type} Order {Order.Status[order.status]} Price: {order.executed.price}')

        self._reset_order(order)

    def _reset_order(self, order):
        data_name = order.data._name
        self.orders[data_name] = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        data_name = trade.data._name
        # print(f"{data_name}: BRUTTO: {trade.pnl}, NETTO: {trade.pnlcomm}, TOTAL: {self.broker.get_value()}")

    def _get_buys_stats(self):
        if self.broker.cash * self.p.max_percentage > self.p.min_amount:
            return 1 / self.p.max_percentage, self.p.max_percentage * self.broker.cash
        elif self.broker.cash > self.p.min_amount:
            return self.broker.cash / self.p.min_amount, self.p.min_amount
        else:
            return 0, 0

    @staticmethod
    @abstractmethod
    def prepare_data(data: pd.DataFrame) -> pd.DataFrame:
        raise NotImplementedError

    @abstractmethod
    def next(self):
        raise NotImplementedError
