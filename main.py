import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

from utils.datareader import read_input_data
from utils.datastats import *


def update_plots(start_idx=0):
    """
    The function is invoked to draw/re-draw the graph. Based on updates on the slider, the graph is updated to depict the
    information for a selected historical period
    :param start_idx:
    :return:
    """
    for subplot in ax:
        subplot.clear()
    filtered_data = security_data.iloc[int(start_idx):]
    ax[0].plot(filtered_data['close'], label='USD-BTC Close Price')
    ax[0].set_title('Historical prices of the cryptocurrency', fontsize = 10)
    ax[1].plot(filtered_data['ewma_vol'])
    ax[1].set_title('EWMA Vol of log returns with lambda = 0.98', fontsize = 10)
    ax[2].plot(filtered_data['adx'])
    ax[2].set_title('Average Directional Index', fontsize = 10)
    ax[3].plot(filtered_data[['positive_directional_indicator', 'negative_directional_indicator']], linewidth=0.5,
               label=['+DI', '-DI'])
    ax[3].set_title('Plotting of +DI & -DI over time', fontsize = 10)
    ax[3].legend()
    fig.autofmt_xdate()
    fig.canvas.draw_idle()
def update_slider(val):
    start_idx = int(datetime_slider.val)
    update_plots(start_idx)

def augment_stock_statistical_information(stock_data):
    stats_generator = DataStatistics(stock_data)
    stock_data['hourly_log_returns'] = stats_generator.generate_log_return()
    stock_data['rolling_vol'] = stats_generator.generate_rolling_volatility()
    stock_data['ewma_vol'] = stats_generator.generate_ewma_volatility()
    stock_data = stats_generator.generate_rolling_directional_indicator()
    return stock_data

security_data = read_input_data('input_data/Bitfinex_BTCUSD_1h.csv')
security_data = augment_stock_statistical_information(security_data)
# security_data.to_csv('usd_btc.csv', index = False)

fig, ax = plt.subplots(4, 1, figsize=(8, 15), sharex=True, linewidth=0.5)
fig.subplots_adjust(bottom=0.2)
update_plots()
ax_timerange = fig.add_axes([0.1, 0.1, 0.85, 0.01])
datetime_slider = Slider(ax=ax_timerange, label='Start', valmin=0, valmax=len(security_data)-1, valinit=0, valstep=1)
datetime_slider.on_changed(update_slider)
plt.show()