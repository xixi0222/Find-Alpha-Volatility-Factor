import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
from collections import defaultdict
from structs import *
from trade import *

class Strategies(MyAccount):
    def __init__(self, price_ts, factor_type=TOTAL_VOL, vol_window=20, \
                 macro_path=MACRO_PATH, strategy_name='volatility_factor',):
        MyAccount.__init__(self, price_ts, strategy_name)
        # cc return
        self.cc_return = np.log(price_ts/price_ts.shift(1)).fillna(0)
        # factor_type
        self.factor_type = factor_type
        # 总波动
        self.total_vol = {}
        # 上行波动
        self.upper_vol = {}
        # 下行波动
        self.lower_vol = {}
        # RSJ
        self.rsj = {}
        # 计算波动因子所需要的窗口长度
        self.vol_window = vol_window
        # alphas from regression
        self.alpha = {}
        # std of alphas from regression
        self.alpha_std = {}
        # std adjusted alphas from regression
        self.alpha_adj = {}
        # kappa1
        self.kappa1 = {}
        # 宏观经济指标
        self.macro = self.read_macro(macro_path)
        # monthly cc return
        self.monthly_cc_return = self.daily_return2monthly_return()
        # alphas from macro
        self.macro_alpha = {}
        # std of alphas from macro
        self.macro_alpha_std = {}
        # std adjusted alphas from regression
        self.macro_alpha_adj = {}
        # kappa2
        self.kappa2 = {}

    def read_macro(self, path):
        # 获得宏观经济指标
        macro = pd.read_excel(path, index_col=0)
        macro.index = pd.to_datetime(macro.index).to_period('M')
        macro.fillna(method='bfill', inplace=True)
        macro.dropna(how='any', inplace=True)
        return macro

    def daily_return2monthly_return(self):
        # monthly cc return
        price_ts = pd.DataFrame(self.price_ts.copy())
        price_ts['dates'] = pd.to_datetime(price_ts.index).to_period('M')
        price_ts.drop_duplicates('dates', keep='last', inplace=True)
        price_ts.index = price_ts['dates']
        price_ts = price_ts['close']
        return(np.log(price_ts / price_ts.shift(1)).fillna(0))

    def generate_strategy(self, time, T=20):
        direction, volume = self.uvol_dvol_rsj(time)
        return direction, volume

    def calculate_kappa1(self, time):
        kappa1_arr = []
        cc_return = self.cc_return
        for index, day in enumerate(cc_return.index[time - KAPPA1_WINDOW + 1:time + 1]):
            if self.alpha_adj[day] * self.alpha[self.today] > 0:
                kappa1_arr.append(self.alpha_adj[day])
        if len(kappa1_arr) > 1:
            kappa1_arr = np.abs(kappa1_arr)
            kappa1_arr = np.array(kappa1_arr) - np.min(kappa1_arr)
        else:
            kappa1_arr = np.abs(kappa1_arr)
            kappa1_arr = np.array(kappa1_arr)
        kappa1_arr /= np.max(kappa1_arr)
        kappa1 = kappa1_arr[-1]
        self.kappa1[self.today] = kappa1

    def calculate_kappa2(self, time):
        kappa2_arr = []
        today_month = str(self.today)[:7]
        macro_alpha_adj_df = self.macro_alpha_adj_df
        try:
            index = macro_alpha_adj_df.index.tolist().index(today_month)
            for _index, day in enumerate(macro_alpha_adj_df.index[index - KAPPA2_WINDOW + 1, index + 1]):
                try:
                    _kappa2 = macro_alpha_adj_df['macro_alpha_adj'].iloc[_index]
                    if _kappa2 * self.alpha[day] > 0:
                        kappa2_arr.append(_kappa2)
                except(KeyError):
                    pass
        except(ValueError):
            pass
        if len(kappa2_arr) > 1:
            kappa2_arr = np.abs(kappa2_arr)
            kappa2_arr = np.array(kappa2_arr) - np.min(kappa2_arr)
            kappa2_arr /= np.max(kappa2_arr)
        elif len(kappa2_arr) == 1:
            kappa2_arr = np.abs(kappa2_arr)
            kappa2_arr /= np.max(kappa2_arr)
        else:
            kappa2_arr = np.array([POSITION_OPEN_SPEED])
        kappa2 = kappa2_arr[-1]
        self.kappa2[self.today] = kappa2

    def uvol_dvol_rsj(self, time):
        available_cash = self.available_cash[self.yesterday]
        price = self.price
        holding = self.holding[self.yesterday]
        func_type = VOLUME_FUNCTION_TYPE
        volume_arr = []
        
        self.calculate_kappa1(time)
        self.calculate_kappa2(time)

        kappa1 = self.kappa1[self.today]
        kappa2 = self.kappa2[self.today]

        if self.alpha[self.today] > 0:
            direction = D_BUY
            volume_arr.append(int(available_cash * (kappa2 + kappa1) / 2 / price))
            volume_arr.append(int(available_cash * kappa1 / price))
            volume_arr.append(int(available_cash * kappa2 * kappa1 / price))
            volume_arr.append(int(available_cash * kappa1 ** 2 / price))
        else:
            direction = D_SELL
            volume_arr.append(int(holding * (kappa2 + kappa1) / 2 / price))
            volume_arr.append(int(holding * kappa1 / price))
            volume_arr.append(int(holding * kappa2 * kappa1 / price))
            volume_arr.append(int(holding * kappa1 ** 2 / price))

        volume = volume_arr[func_type]
        return direction, volume

    def strategy(self, time, T=20):
        self.start_today(time)
        direction, volume = self.generate_strategy(time=time, T=T)
        self.trade(time, direction, volume)

    def calculate_vol_factors(self):
        # Calculate all vol factors
        vol_window = self.vol_window
        cc_return = self.cc_return
        for index, day in enumerate(cc_return.index.to_list()):
            if(index >= vol_window):
                self.total_vol[day] = sum([x ** 2 for x in cc_return[index - vol_window:index]])
                self.upper_vol[day] = sum([x ** 2 for x in cc_return[index - vol_window:index] if x>0])
                self.lower_vol[day] = sum([x ** 2 for x in cc_return[index - vol_window:index] if x<0])
                try:
                    self.rsj[day] = (self.upper_vol[day] - self.lower_vol[day]) / self.total_vol[day]
                except(ZeroDivisionError):
                    self.rsj[day] = 0
            else:
                self.total_vol[day] = 0
                self.upper_vol[day] = 0
                self.lower_vol[day] = 0
                self.rsj[day] = 0

    def FACTOR2factor(self):
        if(self.factor_type==TOTAL_VOL):
            return self.total_vol
        elif(self.factor_type==UPPER_VOL):
            return self.upper_vol
        elif(self.factor_type==LOWER_VOL):
            return self.lower_vol
        elif(self.factor_type==RSJ):
            return self.rsj

    def calculate_alpha1(self, T):
        cc_return = self.cc_return
        factor = list(self.FACTOR2factor().values())
        for index, day in enumerate(cc_return.index.to_list()):
            if (index >= T):
                _model = sm.OLS(
                        cc_return[index - T:index], 
                        sm.add_constant(factor)[index - T:index]
                        ).fit()
                self.alpha[day] = _model.params[0]
                self.alpha_std[day] = np.sqrt(_model.cov_params().iloc[0, 0])
                self.alpha_adj[day] = self.alpha[day] / self.alpha_std[day]
            else:
                self.alpha[day] = 0
                self.alpha_std[day] = 0
                self.alpha_adj[day] = 0

    def calculate_alpha2(self):
        macro_window = MACRO_WINDOW
        monthly_cc_return = pd.DataFrame(self.monthly_cc_return)
        macro = self.macro
        merged = pd.merge(monthly_cc_return, macro, left_index=True, right_index=True)

        for index, day in enumerate(merged.index.to_list()):
            if (index >= macro_window):
                try:
                    _model = sm.OLS(merged[merged.columns[0]].iloc[index - macro_window:index], 
                                    sm.add_constant(merged[merged.columns[1:]].iloc[index - macro_window:index])).fit()
                    self.macro_alpha[day] = _model.params[0]
                    self.macro_alpha_std[day] = np.sqrt(_model.cov_params().iloc[0, 0])
                    self.macro_alpha_adj[day] = self.macro_alpha[day] / self.macro_alpha_std[day]
                except(KeyError):
                    self.macro_alpha[day] = 0
                    self.macro_alpha_std[day] = 0
                    self.macro_alpha_adj[day] = 0
            else:
                self.macro_alpha[day] = 0
                self.macro_alpha_std[day] = 0
                self.macro_alpha_adj[day] = 0

        self.macro_alpha_adj_df = pd.DataFrame(self.macro_alpha_adj, index=['macro_alpha_adj']).T

    def get_factor_table(self):
        factor_table = pd.DataFrame(self.cc_return)
        factor_table.columns = ['return']
        factor_table = factor_table.join(pd.DataFrame(self.FACTOR2factor(),\
            index=['factor_type' + str(self.factor_type)]).T)
        factor_table = factor_table.join(pd.DataFrame(self.alpha_adj,\
            index=['alpha_adj']).T)
        factor_table = factor_table.join(pd.DataFrame(self.kappa1,\
            index=['kappa1_adj']).T)
        factor_table = factor_table.join(pd.DataFrame(self.kappa2,\
            index=['kappa2_adj']).T)
        self.factor_table = factor_table
        return factor_table

    def trade_table2dataframe(self):
        trade_table = pd.DataFrame(self.trade_table)
        factor_table = self.get_factor_table()
        trade_table = trade_table.join(factor_table)
        return trade_table