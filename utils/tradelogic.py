import numpy as np
def get_binomial_tree(initial_price, step_size):
    u = initial_price
    u1 = initial_price + step_size
    u0 = initial_price - step_size
    u11 = u1 + step_size
    u00 = u0 - step_size
    binomial_tree = [u, u1, u0, u11, u00]
    return binomial_tree

class TradeIndicators:
    def __init__(self, stock_prices, step_type):
        self.stock_prices = stock_prices
        self.step_type = step_type
    def check_price_path_probabilities(self):
        stock_prices = self.stock_prices
        step_type = self.step_type
        u1_counter = 0
        u11_counter = 0
        u10_counter = 0
        u0_counter = 0
        u01_counter = 0
        u00_counter = 0
        for i in range(len(stock_prices)):
            if stock_prices.iloc[i]['cross_over'] == 1:
                initial_stock_price_at_cross_over = stock_prices.iloc[i]['close']
                if step_type == 'ATR':
                    step_size = stock_prices.iloc[i]['atr']/2
                    # print('ATR :', stock_prices.iloc[i]['atr'])
                elif step_type == 'EWMA_VOL':
                    step_size = stock_prices.iloc[i]['ewma_vol_step']
                else:
                    step_size = stock_prices.iloc[i]['atr']
                [u, u1, u0, u11, u00] = get_binomial_tree(initial_stock_price_at_cross_over, step_size)

                for j in range(i+1, len(stock_prices)):
                    future_high_price = stock_prices.iloc[j]['high']
                    future_low_price = stock_prices.iloc[j]['low']
                    # print('Value of :', i, future_high_price, future_low_price)
                    while stock_prices.iloc[j]['trade_cycle'] == stock_prices.iloc[j + 1]['trade_cycle']:

                        l2_future_high_price = stock_prices.iloc[j]['high']
                        l2_future_low_price = stock_prices.iloc[j]['low']
                        if future_high_price >= u1:
                            u1_counter += 1
                            if l2_future_high_price >= u11:
                                u11_counter+=1
                                break
                            elif l2_future_low_price <= u:
                                u10_counter+=1
                                break
                        if future_low_price <= u0:
                            u0_counter += 1
                            if future_low_price <= u00:
                                u00_counter+=1
                                break
                            elif l2_future_high_price >= u:
                                u01_counter+=1
                                break
                        j += 1
                    i = j
                    break

        # We calculate the probability of the counter being hit when the positive crossover point is hit
        u1_counter_prob = u1_counter/np.sum(stock_prices['cross_over'] == 1)
        u11_counter_prob = u11_counter/np.sum(stock_prices['cross_over'] == 1)
        u10_counter_prob = u10_counter / np.sum(stock_prices['cross_over'] == 1)
        u0_counter_prob = u0_counter / np.sum(stock_prices['cross_over'] == 1)
        u00_counter_prob = u00_counter / np.sum(stock_prices['cross_over'] == 1)
        u01_counter_prob = u01_counter / np.sum(stock_prices['cross_over'] == 1)
        cross_over_probability_matrix = [u11_counter_prob, u10_counter_prob, u00_counter_prob, u01_counter_prob]
        return cross_over_probability_matrix



