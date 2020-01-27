# 初始资金
INITIAL_CASH = 500000

# 买入
D_BUY = '1'
# 卖出
D_SELL = '-1'

# 默认建仓速度
POSITION_OPEN_SPEED = 0.5

# 宏观窗口大小
MACRO_WINDOW = 24
# 回归窗口大小
REGRESSION_WINDOW = [[20], [60, 120], [10, 20, 30, 60, 120]]
KAPPA1_WINDOW = 10
KAPPA2_WINDOW = 10

# 单笔交易佣金率
COMMISSION = 0.

# Plot style
PLOT_STYLE = 'seaborn'

# Trade Strategy
# RAMDON_NUMBER = 1
# CHASE_HIGH_SELL_LOW = 2
# SINGLE_FACTOR = 3
UVOL_DVOL_RSJ = 4

# Time Range of Data Set
"""
Trainning set: find the optimal strategy
Test set: test the chosen optimal strategy
Better to split these two set, no overlap.
"""

TRAINNING_SET_START_DATE = 484
TRAINNING_SET_END_DATE = 1300
# TEST_SET_START_DATE = 484
# TEST_SET_END_DATE = 3640

# 选择一个因子，用在决策中得到price和volume
TOTAL_VOL = 1
UPPER_VOL = 2
LOWER_VOL = 3
RSJ = 4

MACRO_PATH = 'MACRO.xlsx'
PRICE_PATH = 'CSI500.csv'

VOLUME_FUNCTION_TYPE = 0
PLOT_FEATURE_TYPE = [0,1,2]