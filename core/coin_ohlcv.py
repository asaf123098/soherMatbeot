import pandas as pd
from core import Interval
from dataclasses import dataclass


@dataclass
class CoinOHLCV:
    coin: str
    chart: pd.DataFrame
