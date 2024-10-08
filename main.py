import time
import matplotlib.pyplot as plt
from utils.datareader import read_input_data
from utils.datastats import *

usd_btc_data = read_input_data('input_data/Bitfinex_BTCUSD_1h.csv')
stats_generator = DataStatistics(usd_btc_data)
usd_btc_data['hourly_log_returns'] = stats_generator.generate_log_return()
usd_btc_data['rolling_vol'] = stats_generator.generate_rolling_volatility()
usd_btc_data['ewma_vol'] = stats_generator.generate_ewma_volatility()
# usd_btc_data['atr'] = stats_generator.generate_rolling_average_true_range()
data = stats_generator.generate_rolling_directional_indicator()
data.to_csv('usd_btc.csv', index = False)
# Extract the unique years in the data set. This is just to make the rendering of the graph faster so that there are
# limited number of xticks
years = usd_btc_data.index.year.unique().tolist()
print('Printing subplots')
fig,ax = plt.subplots(4, 1, figsize = (10,15), sharex=True, linewidth = 0.5)
ax[0].plot(usd_btc_data['close'])
ax[0].set_xticklabels(years)
ax[1].plot(usd_btc_data['rolling_vol'])
ax[2].plot(usd_btc_data['ewma_vol'])
ax[3].plot(usd_btc_data['adx'])
plt.tight_layout()
plt.show()
print('Show Plot')
# reader = DataClass(stock_data_folder)
end_time = time.time()
