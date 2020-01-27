import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
from collections import defaultdict
from structs import *

class MyAccount(object):

    def __init__(self, price_ts, strategy_name):
        # 交易当日日期
        self.today = 0
        # 当日价格
        self.price = 0
        # 交易昨日日期
        self.yesterday = 0
        # 仓位（必须为正）
        self.position = defaultdict(int)
        # 初始资金
        self.total_cash = INITIAL_CASH
        # 可用资金
        self.available_cash = defaultdict(lambda: self.total_cash)
        # 换手次数
        self.trade_times = defaultdict(int)
        # 最大回撤
        self.maximum_drawback = 0
        # 佣金
        self.commission = defaultdict(int)
        # CSI500价格数据
        self.price_ts = price_ts
        # Profit and Loss (PnL)
        self.PnL = defaultdict(int)
        # 持仓价值
        self.holding = defaultdict(int)
        # total assets
        self.total_assets = defaultdict(lambda: self.total_cash)
        # 局部最高点
        self.local_maximum = 0
        # 局部最高点是否更新
        self.local_max_update = 0
        # 局部最低点
        self.local_minimum = 0
        # trade direction
        self.direction = defaultdict(int)
        # trade volume
        self.volume = defaultdict(int)
        # trade table
        self.trade_table = defaultdict(dict)
        # trade strategy name
        self.strategy_name = strategy_name

    def time2today(self, time):
        # time: int, the index of the Series
        # today: time period, the value of the Series
        self.today = self.price_ts.index[time]

    def time2yesterday(self, time):
        if((time + 1) < len(self.price_ts)):
            self.yesterday = self.price_ts.index[time - 1]

    def get_current_price(self):
        self.price = self.price_ts[self.today]

    def start_today(self, time):
        # Save the time period of today and yesterday
        self.time2today(time)
        self.time2yesterday(time)
        self.get_current_price()

    def trade(self, time, direction, volume):
        direction = int(direction)
        price = self.price
        yesterday = self.yesterday
        today = self.today
        # available cash for trading for today
        available_cash = self.available_cash[yesterday]
        # position holding for trading for today
        position = self.position[yesterday]

        if (direction == 1 and available_cash - volume * price < 0):
            # If we don't have enough money, we spend them all
            volume = int(available_cash / price)
        if (direction == -1 and position - volume < 0):
            # If we don't have enough instrument, we sell them all
            volume = int(position)

        # Do the trading...
        order = {'date': today, 
                'direction': direction, 
                'price': price, 
                'volume': volume, 
                'available_cash_yesterday': self.available_cash[yesterday]}

        # Do the accounting
        self.position[today] = self.position[yesterday] + direction * volume
        self.trade_times[today] = self.trade_times[yesterday] + int(volume > 0)
        self.commission[today] = self.commission[yesterday] + price * volume * COMMISSION
        self.available_cash[today] = self.available_cash[yesterday] \
                - direction * volume * price + price * volume * COMMISSION
        self.holding[today] = price * self.position[today]
        self.PnL[today] = self.holding[today] + self.available_cash[today] - self.total_cash
        self.total_assets[today] = self.holding[today] + self.available_cash[today]
        self.direction[today] = direction
        self.volume[today] = volume
        self.cal_maximum_drawback()

    def cal_maximum_drawback(self):
        # Calculate the maximum drawback
        today = self.today
        if self.PnL[today] > self.local_maximum:
            self.local_maximum = self.PnL[today]
        if self.local_maximum != 0 and self.local_maximum != self.PnL[today]:
            drawback = (self.local_maximum - self.PnL[today]) / (self.local_maximum + self.total_cash)
            self.maximum_drawback = max(self.maximum_drawback, drawback)

    def get_trade_table(self):
        trade_table = {}
        trade_table['position'] = self.position
        trade_table['available cash'] = self.available_cash
        trade_table['holding'] = self.holding
        trade_table['PnL'] = self.PnL
        trade_table['trade_times'] = self.trade_times
        trade_table['total_assets'] = self.total_assets
        trade_table['direction'] = self.direction
        trade_table['volume'] = self.volume
        self.trade_table = trade_table

    def get_statistics(self):
        trade_table = pd.DataFrame(self.trade_table)
        statistics = pd.DataFrame(index=['stats'])
        statistics['PnL'] = trade_table['PnL'].iloc[-1]
        statistics['Return'] = statistics['PnL'] / self.total_cash
        statistics['PnL_volatility'] = trade_table['PnL'].std()
        statistics['trade_times'] = trade_table['trade_times'].iloc[-1]
        statistics['turnover_rate'] \
                = statistics['trade_times'] / len(self.price_ts)
        statistics['max_drawback'] = self.maximum_drawback
        return statistics.T