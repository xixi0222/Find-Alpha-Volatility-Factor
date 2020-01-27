import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
from collections import defaultdict
from structs import *
from strategy import *
from visualization import *

if __name__ == "__main__":
    # set plot style
    plt.style.use(PLOT_STYLE)
    # set strategy name
    strategy_name = UVOL_DVOL_RSJ

    # Get window values
    windows_list_type = 2
    windows = REGRESSION_WINDOW[windows_list_type]

    # File path
    macro_path = MACRO_PATH
    price_path = PRICE_PATH

    factor_type = RSJ
    plot_feature_type = PLOT_FEATURE_TYPE

    # data reading
    csi500 = pd.read_csv(price_path, index_col=0)
    csi500.index = pd.to_datetime(csi500.index)
    # close price, from start day to end day
    price_ts = csi500['close'][::-1]

    for vol_window in windows:        

        vol_strategy = Strategies(price_ts, factor_type=factor_type, \
            vol_window=vol_window, macro_path=macro_path)
        vol_strategy.calculate_vol_factors()
        vol_strategy.calculate_alpha1(T=vol_window)
        vol_strategy.calculate_alpha2()

        time = TRAINNING_SET_START_DATE
        end_time = TRAINNING_SET_END_DATE

        while time <= end_time:
            vol_strategy.strategy(time, T=vol_window)
            time += 1
        vol_strategy.get_trade_table()
        trade_table = vol_strategy.trade_table2dataframe()
        statistics = vol_strategy.get_statistics()
        with pd.ExcelWriter("../plot/" + str(strategy_name) + '_winsT_' + \
            str(vol_window) +'_fcType_' + str(factor_type) + ".xlsx") as writer:
            trade_table.to_excel(writer, sheet_name='trade_table')
            statistics.to_excel(writer, sheet_name='statistics')
        
        # Plot charts & Output into files for visualization
        visualization = Visualization(vol_strategy)
        for feature_type in plot_feature_type:
            visualization.plot_chart(feature_type, windows_len=str(vol_window), factor_type=str(factor_type))
        visualization.plot_assets_cmp(windows_len=str(vol_window), factor_type=str(factor_type))
