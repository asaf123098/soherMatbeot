import os
import json
from os.path import join, isdir

from constants import INTERVAL_OPTS
from data_fetchers.coin_data_fetcher import COINS_DATA_PATH, STOCKS_DATA_PATH
from strategies.examples import ThreeEmaStochRsi, ParabolicSAR_SMA200, IchiStcCmf, SuperTrendStochEma200, \
    StochRsiMACD, ParabolicSAR_EMA200_MACD, DecisionTreeAI
from use_local_data import use_local_data, use_local_stocks_data
from strategy_tester import StrategyTester

RESULTS_FOLDER = join(".", "test_results")


def main():
    strategy = ThreeEmaStochRsi
    new_dir_path = join(RESULTS_FOLDER, strategy.__name__)

    if not isdir(new_dir_path):
        os.makedirs(new_dir_path)

    for interval in INTERVAL_OPTS:
        data = use_local_data(interval, COINS_DATA_PATH)
        # data = use_local_stocks_data(interval, STOCKS_DATA_PATH_DATA_PATH)
        strat_tester = StrategyTester(strategy, data, interval=interval)
        analysis = strat_tester.get_analysis()
        print(interval, analysis["daily_increase_percentage"], analysis["total_amount"], analysis["starting_amount"])

        with open(join(new_dir_path, f"{interval}.json"), "w") as f:
            json.dump(analysis, f, indent=4)

        strat_tester.save_plot(join(new_dir_path, f"{interval}.png"))


if __name__ == '__main__':
    main()
