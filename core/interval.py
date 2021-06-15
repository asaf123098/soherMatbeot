import re
from abc import ABCMeta
from typing import Tuple
from datetime import datetime, timedelta

from constants import INTERVAL_OPTS


REGEX = "(\d{,2})([a-zA-Z])"


class Interval(object):
    @staticmethod
    def calculate_start_date_timestamp(interval: str, n_candles: int, end_date: datetime) -> int:
        Interval.validate_interval(interval)
        n_interval, interval_type = Interval._separate_amount_type(interval)
        time_back = n_interval * n_candles
        return Interval._get_start_date_timestamp_by_interval_type(time_back, interval_type, end_date)

    @staticmethod
    def validate_interval(interval):
        if interval not in INTERVAL_OPTS:
            raise ValueError(f"Unknown interval {interval}")

    @staticmethod
    def _get_start_date_timestamp_by_interval_type(time_back: int, interval_type: str, end_date: datetime) -> int:
        start_date = end_date

        if interval_type == 'm':
            start_date = end_date - timedelta(minutes=time_back)
        elif interval_type == "h":
            start_date = end_date - timedelta(hours=time_back)
        elif interval_type == "d":
            start_date = end_date - timedelta(days=time_back)
        elif interval_type == "w":
            start_date = end_date - timedelta(weeks=time_back)
        elif interval_type == "M":
            start_date = end_date - timedelta(days=time_back * 30)
        else:
            ValueError("Wrong Interval")

        start_date_timestamp = int(start_date.timestamp()) * 1000
        return start_date_timestamp

    @staticmethod
    def _separate_amount_type(interval: str) -> Tuple[int, str]:
        interval_info = re.compile(REGEX).findall(interval)

        if not interval_info:
            raise ValueError("Something wrong with interval")

        n_interval, interval_type = interval_info[0]
        return int(n_interval), interval_type





