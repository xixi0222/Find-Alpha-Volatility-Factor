# Find-Alpha-Volatility-Factor

#### Brief Introduction
1. Use total, upper, down, relative volatility factors to find **Alpha**.   
2. Define own functions for trading direction & volume.   
3. Implement whole **trading process** & back-test with daily frequency.   
4. Calculate and record important financial data.   
5. Plot charts & Output trading financial data into files for visualization.  

#### Details
1. Volatility factors:
  * **Total Volatility (VOL)**:  
  It measures the total volatility of the instrument. With higher volatility, it demands for higher return.
  * **Upper/Down Volatility (UVOL/DVOL)**:  
  It measures the volatility by trend (go up or down) of the instrument. With higher unilateral volatility, the price volatility is higher in this side.
  * **Relative Volatility (RSJ)**: *𝐑𝐒𝐉 = 𝐔𝐕𝐎𝐋 − 𝐃𝐕𝐎𝐋*  
  It measures the relative volatility of the instrument. With higher absolute value of relative volatility, it shows short-term pressure (sharp long and steady short power), and lower future return.
2. Financial data: Holding, Position, Total assets, Available cash, Profit and Loss, Return, Sharp's retio, volatility...  
3. Trading records: Trading direction, Trading volume, Turnover rate, Trading times, Maximum drawdown...  

#### Results
1. RSJ has the best result in most years.  
2. Volatility Factors Windows: **Shorter** Time are better. 5 days, 10 days, 15 days windows perform better than long-time windows.  
3. Macro Factors Windows: **Longer** Time are better. 24 months provides a better PnL, return and maximum drawdown.  
4. Period Analysis:  
 * This model follows the trend.
 * It has a conservative approach. When the market is very volatile, it follows the trend but does not go as high or as low as CSI500. 
 * It needs improvement in markets with high volatility.
 * It Performs good in stable conditions. Comparing with the last two years, it overperforms the Chinese market by 30%.
 

*Data: CSI500 Index  
Data Source: Wind*
