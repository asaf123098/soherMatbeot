import pickle
import numpy as np
import pandas as pd
import pandas_ta as ta
import backtrader as bt
from backtrader import feeds
from strategies.strategy_abs import StrategyAbs

RISK = 1.5
N_CANDLES_BACK = 10
MODEL_PATH = r"C:\Users\ofeki\Desktop\CryptoAITests\Models\trend_model_{}.pickle"

class DecisionTreeAI(StrategyAbs):
    def __init__(self, interval: str):
        super(DecisionTreeAI, self).__init__()

        with open(MODEL_PATH.format(interval), "rb") as f:
            self.model = pickle.load(f)

    @staticmethod
    def prepare_data(data: pd.DataFrame) -> pd.DataFrame:
        data_copy = data.copy()
        indicators = [
            "macd", "rsi", "stoch", "squeeze", "roc", "supertrend", "entropy", "kurtosis", "mad", "skew",
            "stdev", "variance", "zscore", "adx", "aroon", "psar", "dpo", "chop", "atr", "massi", "ui", "rvi", "adosc",
            "aobv", "cmf"
        ]
        drop_columns = [
            "MACD_12_26_9", "MACDs_12_26_9", "SUPERT_7_3.0", "SUPERTl_7_3.0", "SUPERTs_7_3.0", "PSARl_0.02_0.2",
            "PSARs_0.02_0.2",
            "PSARaf_0.02_0.2", "PSARr_0.02_0.2", 'OBV', 'OBV_min_2', 'OBV_max_2', 'OBVe_4', 'OBVe_12'
        ]
        for ind in indicators:
            if ind == 'dpo':
                data_copy.ta.dpo(centered=False, append=True)
            else:
                getattr(data_copy.ta, ind)(append=True)

        data_copy["stoch_osch"] = data_copy["STOCHk_14_3_3"] - data_copy["STOCHd_14_3_3"]
        data_copy["psar"] = data_copy["PSARl_0.02_0.2"].notna()
        data_copy.drop(columns=drop_columns, inplace=True)
        return data_copy


    def _get_row_for_model(self, data: feeds):
        row = [
            data.macdh_12_26_9[0], data.rsi_14[0], data.stochk_14_3_3[0], data.stochd_14_3_3[0],
            data.sqz_20_20_20_15[0], data.sqz_on[0], data.sqz_off[0], data.sqz_no[0], data.roc_10[0],
            data.supertd_7_30[0], data.entp_10[0], data.kurt_30[0], data.mad_30[0], data.skew_30[0],
            data.stdev_30[0], data.var_30[0], data.z_30[0], data.adx_14[0], data.dmp_14[0], data.dmn_14[0],
            data.aroond_14[0], data.aroonu_14[0], data.aroonosc_14[0], data.dpo_20[0], data.chop_14_1_100[0],
            data.atrr_14[0], data.massi_9_25[0], data.ui_14[0], data.rvi_14[0], data.adosc_3_10[0], data.aobv_lr_2[0],
            data.aobv_sr_2[0], data.cmf_20[0], data.stoch_osch[0], data.psar[0]
        ]
        return row

    def buy_signal(self, data: feeds):
        row = self._get_row_for_model(data)
        row_for_model = np.array(row).reshape(1, -1)

        if np.isnan(row_for_model.sum()):
            return False

        if self.model.predict(np.array(row_for_model).reshape(1, -1))[0] == 1:
            return True
        return False

    def sell_signal(self, data: feeds):
        row_for_model = self._get_row_for_model(data)

        if self.model.predict(np.array(row_for_model).reshape(1, -1))[0] == 0:
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
                if self.buy_signal(data):
                    price = data.close[0]
                    self.buy(
                        data=data,
                        size=(amount / price),
                        exectype=bt.Order.Market
                    )

            elif position.size > 0:
                if self.sell_signal(data):
                    self.close(data=data)
