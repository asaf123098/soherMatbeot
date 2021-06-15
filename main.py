import os
import json
from constants import INTERVAL_OPTS
from strategies.examples import ThreeEmaStochRsi, ParabolicSAR_SMA200, IchiStcCmf, SuperTrendStochEma200, \
    StochRsiMACD, ParabolicSAR_EMA200_MACD, DecisionTreeAI
from data_fetcher import fetch_data
from strategy_tester import StrategyTester


RESULTS_FOLDER = ".\\test_results"

def main():
    strategy = DecisionTreeAI
    new_dir_path = RESULTS_FOLDER + "\\" + strategy.__name__

    if not os.path.isdir(new_dir_path):
        os.mkdir(new_dir_path)

    for interval in INTERVAL_OPTS:
        if interval != "5m":
            continue

        coins_data = fetch_data(interval)
        strat_tester = StrategyTester(strategy, coins_data, interval=interval)
        analysis = strat_tester.get_analysis()
        print(interval, analysis["daily_increase_percentage"], analysis["total_amount"], analysis["starting_amount"])

        with open(new_dir_path + f"\\{interval}.json", "w") as f:
            json.dump(analysis, f, indent=4)

        strat_tester.save_plot(new_dir_path + f"\\{interval}.png")


if __name__ == '__main__':
    main()

