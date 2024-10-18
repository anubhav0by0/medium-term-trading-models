import numpy as np
import pandas as pd
from arch import arch_model
def get_binomial_tree(initial_price, step_size):
    u = initial_price
    u1 = initial_price + step_size
    u0 = initial_price - step_size
    u11 = u1 + step_size
    u00 = u0 - step_size
    binomial_tree = [u, u1, u0, u11, u00]
    return binomial_tree

class DataStatistics:
    def __init__(self, stock_dataframe, rolling_window = 10, forecast_period = 10, adx_window = 24, ewma_lambda = 0.98):
        """"
        The class is instantiated with a stock values dataframe which contains the OLHC data,
        the volume all indexed with datetime with an interval of 1H
        """
        self.stock_details = stock_dataframe
        self.close_prices = stock_dataframe['close']
        self.stock_returns = self.generate_log_return()
        self.rolling_window = rolling_window * 24
        self.forecast_period = forecast_period
        self.adx_window = adx_window
        self.ewma_lambda = ewma_lambda
    def generate_log_return(self):
        """
        This method when invoked returns the timeseries of the log-returns
        :return:
        """
        prices = self.close_prices
        return np.log(prices/prices.shift(1))
    def generate_rolling_volatility(self):
        """
        The method when invoked returns the 1-Hr rolling period volatility from a timeseries of returns
        which are in 1hour intervals
        :return:
        """
        return self.stock_returns.rolling(self.rolling_window).std()
    def forecast_garch_volatility(self):
        garch_model = arch_model(self.stock_returns, vol='GARCH', p=1, q=1)
        garch_model.fit(disp='off')
        vol_forecast = garch_model.forecast(horizon=10)
        return vol_forecast

    def generate_ewma_volatility(self):
        """
        Generate the Exponential Weighted Moving Average Volatility
        :return: a dataframe consisting of the stock data along with the forecasted volatility
        """
        # The lambda value for EWMA is the smoothing factor
        # A typical value for lambda (decay factor) is as follows :
        # Daily data: λ=0.94
        # Hourly data: λ=0.97 to 0.99
        # Weekly data: 𝜆 = 0.90
        ewma_lambda = self.ewma_lambda
        stock_returns = self.stock_details['hourly_log_returns']
        ewma_variance = stock_returns.ewm(span=(1/(1-ewma_lambda)), adjust=False).var()
        return np.sqrt(ewma_variance)

    def generate_rolling_average_true_range(self):
        stock_data = self.stock_details
        adx_window = self.adx_window
        high, low, prev_close = stock_data['high'], stock_data['low'], stock_data['close']
        true_range = pd.concat([high-low, high-prev_close.shift(1), low-prev_close.shift(1)], axis=1).max(axis=1)
        return true_range.rolling(adx_window).mean()

    def generate_rolling_directional_indicator(self):
        stock_data = self.stock_details
        adx_window = self.adx_window
        high, low = stock_data['high'], stock_data['low']
        high_movement = high.diff()
        low_movement = low.diff()
        high_movement.loc[(high_movement<=0)|(high_movement<=low_movement)] = 0
        low_movement.loc[(low_movement<=0)|(low_movement<=high_movement)] = 0
        stock_data['positive_directional_movement'] = high_movement
        stock_data['negative_directional_movement'] = low_movement
        stock_data['atr'] = self.generate_rolling_average_true_range()
        stock_data['positive_directional_indicator'] = (stock_data['positive_directional_movement'].rolling(adx_window).mean()/
                                                        stock_data['atr'])
        stock_data['negative_directional_indicator'] = (stock_data['negative_directional_movement'].rolling(adx_window).mean() /
                                                        stock_data['atr'])
        stock_data['dx'] = (np.abs(stock_data['positive_directional_indicator'] - stock_data['negative_directional_indicator'])/
                            (stock_data['positive_directional_indicator'] + stock_data['negative_directional_indicator'])) * 100
        stock_data['adx'] = stock_data['dx'].rolling(adx_window).mean()
        stock_data['cross_over'] = np.where((stock_data['positive_directional_indicator']>stock_data['negative_directional_indicator']) &
                                            (stock_data['positive_directional_indicator'].shift(1)<=stock_data['negative_directional_indicator'].shift(1)) &
                                            (stock_data['adx']>20), 1, 0)
        stock_data['cross_over'] = np.where((stock_data['positive_directional_indicator']<stock_data['negative_directional_indicator']) &
                                            (stock_data['positive_directional_indicator'].shift(1)>=stock_data['negative_directional_indicator'].shift(1)) &
                                            (stock_data['adx']>20), -1, 0) + stock_data['cross_over']
        stock_data['trade_cycle'] = stock_data['cross_over']
        stock_data['trade_cycle'] = stock_data['trade_cycle'].replace(0, np.nan)
        stock_data['trade_cycle'] = stock_data['trade_cycle'].ffill(axis=0)
        return stock_data


