from backtrader.feeds import PandasData


class PandasFeedCreator(object):
    @staticmethod
    def to_pandas_feed(data):
        class PandasDataFeed(PandasData):
            lines = tuple((col_name.replace(".", "").lower() for col_name in data.columns))
            params = (
                (col_name.replace(".", "").lower(), col_name) for col_name in data.columns
            )

        return PandasDataFeed(dataname=data, plot=False)
