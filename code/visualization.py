import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
from collections import defaultdict
from structs import *

class Visualization(object):
    def __init__(self, strategy_obj):
        self.trade_table = strategy_obj.trade_table
        self.total_cash = strategy_obj.total_cash
        self.price_ts = strategy_obj.price_ts
        self.maximum_drawback = strategy_obj.maximum_drawback
        self.strategy_name = strategy_obj.strategy_name
        self.total_assets = strategy_obj.total_assets
        self.position = strategy_obj.position
        self.PnL = strategy_obj.PnL
        self.available_cash = strategy_obj.available_cash
        self.holding = strategy_obj.holding

    def plot_chart(self, feature_type=0, kind='line', figsize=(9, 6), windows_len='', factor_type=''):
        feature_names = ['total_assets', 'position', 'PnL', 'available_cash', 'holding']
        features = []
        features.append(self.total_assets)
        features.append(self.position)
        features.append(self.PnL)
        features.append(self.available_cash)
        features.append(self.holding)

        feature = features[feature_type]
        feature_name = feature_names[feature_type]

        df = pd.DataFrame(feature, index=[feature_name]).T
        fig, ax = plt.subplots(figsize=figsize)
        df.plot(ax=ax, kind=kind)
        plt.savefig("../plot/"+ str(self.strategy_name) + str(feature_name) + '_winsT_' \
                    + windows_len +'_fcType_' + factor_type + ".png")
        return ax
    
    def plot_assets_cmp(self, kind='line', figsize=(9, 6), windows_len='', factor_type=''):
        df = pd.DataFrame(self.total_assets, index=['Backtest']).T
        fig, ax = plt.subplots(figsize=figsize)
        compare_df = self.price_ts.iloc[TRAINNING_SET_START_DATE : TRAINNING_SET_END_DATE + 1] / \
                     self.price_ts.iloc[TRAINNING_SET_START_DATE] * self.total_cash
        compare_df.plot(ax=ax, kind=kind, label='CSI500')
        df.plot(ax=ax, kind=kind, label='Backtest')
        plt.legend(loc=0)
        ax.set_title("Total Assets")
        plt.savefig("../plot/" + '_winsT_' + windows_len +'_fcType_' + \
                    factor_type + ".png")
        return ax
