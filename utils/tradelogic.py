import numpy as np
import cvxpy as cp
import pandas as pd

from utils.datastats import get_binomial_tree


def check_node(trade_block, step_type):
    exit_loops = False
    trade_exit_pl_share = 0
    # counters for positive crossovers
    u1_counter, u11_counter, u10_counter, u0_counter, u00_counter, u01_counter = 0, 0, 0, 0, 0, 0
    # counters for negative crossover
    _u1_counter, _u11_counter, _u10_counter, _u0_counter, _u00_counter, _u01_counter = 0, 0, 0, 0, 0, 0
    end_nodes = ['u1', 'u0', 'u11', 'u10', 'u01', 'u00']
    # df_end_nodes = pd.DataFrame(end_nodes)
    first_row = trade_block.iloc[[0]].copy()
    first_row[end_nodes] = None
    # first_row = pd.concat([first_row,df_end_nodes], axis=1)
    initial_stock_price_at_cross_over = trade_block.iloc[0]['close']
    cross_over_indicator = trade_block.iloc[0]['trade_cycle']
    if step_type == 'ATR':
        step_size = trade_block.iloc[0]['atr'] / 2
    elif step_type == 'EWMA_VOL':
        step_size = trade_block.iloc[0]['ewma_vol_step']
    else:
        step_size = trade_block.iloc[0]['atr']
    [u, u1, u0, u11, u00] = get_binomial_tree(initial_stock_price_at_cross_over, step_size)
    for i in range(1,len(trade_block)):
        node1_high_price = trade_block.iloc[i]['high']
        node1_low_price = trade_block.iloc[i]['low']
        if node1_high_price >= u1:
            first_row.loc[first_row.index[0],'u1'] = 1
            if cross_over_indicator == 1:
                u1_counter += 1
            elif cross_over_indicator == -1:
                _u1_counter += 1
            for j in range(i+1, len(trade_block)):
                node2_high_price = trade_block.iloc[j]['high']
                node2_low_price = trade_block.iloc[j]['low']
                if node2_high_price >= u11:
                    first_row.loc[first_row.index[0],'u11'] = 1
                    if cross_over_indicator == 1:
                        u11_counter += 1
                    elif cross_over_indicator == -1:
                        _u11_counter += 1
                    exit_loops = True
                    break
                elif node2_low_price <= u:
                    first_row.loc[first_row.index[0],'u10'] = 1
                    if cross_over_indicator == 1:
                        u10_counter += 1
                    elif cross_over_indicator == -1:
                        _u10_counter += 1
                    exit_loops = True
                    break
        elif node1_low_price <= u0:
            first_row.loc[first_row.index[0],'u0'] = 1
            if cross_over_indicator == 1:
                u0_counter += 1
            elif cross_over_indicator == -1:
                _u0_counter += 1
            for j in range(i+1, len(trade_block)):
                node2_high_price = trade_block.iloc[j]['high']
                node2_low_price = trade_block.iloc[j]['low']
                if node2_high_price >= u:
                    first_row.loc[first_row.index[0],'u01'] = 1
                    if cross_over_indicator == 1:
                        u01_counter += 1
                    elif cross_over_indicator == -1:
                        _u01_counter += 1
                    exit_loops = True
                    break
                elif node2_low_price <= u00:
                    first_row.loc[first_row.index[0],'u00'] = 1
                    if cross_over_indicator == 1:
                        u00_counter += 1
                    elif cross_over_indicator == -1:
                        _u00_counter += 1
                    exit_loops = True
                    break

        if exit_loops:
            break
    positive_crossover_counter = np.array([u1_counter, u0_counter, u11_counter, u10_counter, u01_counter, u00_counter])
    negative_crossover_counter = np.array([_u1_counter, _u0_counter, _u11_counter, _u10_counter, _u01_counter, _u00_counter])
    if np.all(positive_crossover_counter == 0) | np.all(negative_crossover_counter == 0):
        trade_exit_pl_share = trade_block.iloc[-1]['close'] - trade_block.iloc[0]['open']
    return positive_crossover_counter, negative_crossover_counter, trade_exit_pl_share, first_row

class TradeIndicators:
    def __init__(self, stock_prices, step_type):
        self.stock_prices = stock_prices
        self.step_type = step_type
    def check_price_path_probabilities(self):
        stock_prices = self.stock_prices
        step_type = self.step_type
        # Group the trades
        stock_prices['trade_group'] = stock_prices['cross_over'].abs().cumsum()
        print(len(stock_prices['trade_group'].unique()))
        cumulative_positive_crossover_counter = [0, 0, 0, 0, 0, 0]
        cumulative_negative_crossover_counter = [0, 0, 0, 0, 0, 0]
        no_of_pos_crossover = len(stock_prices.loc[stock_prices['cross_over']==1])
        no_of_neg_crossover = len(stock_prices.loc[stock_prices['cross_over']==-1])
        cum_trade_pnl = 0
        cross_over_stock_prices = pd.DataFrame()
        for trade_group in stock_prices['trade_group'].unique():
            trade_block = stock_prices[stock_prices['trade_group']==trade_group]
            positive_crossover_counter, negative_crossover_counter, trade_pnl, first_row = check_node(trade_block, step_type)
            cross_over_stock_prices = pd.concat([cross_over_stock_prices, first_row], axis=0)
            cumulative_positive_crossover_counter += positive_crossover_counter
            cumulative_negative_crossover_counter += negative_crossover_counter
            cum_trade_pnl += trade_pnl

        u1_counter, u0_counter, u11_counter, u10_counter, u01_counter, u00_counter = cumulative_positive_crossover_counter
        _u1_counter, _u0_counter, _u11_counter, _u10_counter, _u01_counter, _u00_counter = cumulative_negative_crossover_counter
        # We calculate the probability of the counter being hit when the positive crossover point is hit
        positive_cross_over_probability_matrix = np.round(cumulative_positive_crossover_counter/no_of_pos_crossover,4)
        negative_cross_over_probability_matrix = np.round(cumulative_negative_crossover_counter/no_of_neg_crossover, 4)
        # cross_over_probability_matrix /= sum(cross_over_probability_matrix)
        print('No of +ve crossovers %3d with \nu1 = %3d -> u11 = %3d, u10 = %3d, \n'
              'u0 = %3d -> u01 = %3d, u00 = %3d'% (no_of_pos_crossover, u1_counter, u11_counter, u10_counter,
                                                                u0_counter, u01_counter, u00_counter))
        print('No of -ve crossovers %3d with \nu1 = %3d -> u11 = %3d, u10 = %3d, \n'
              'u0 = %3d -> u01 = %3d, u00 = %3d' % (no_of_neg_crossover, _u1_counter, _u11_counter, _u10_counter,
                                                    _u0_counter, _u01_counter, _u00_counter))
        # return cumulative_positive_crossover_counter, cumulative_negative_crossover_counter
        positive_node2_cross_over_probability = positive_cross_over_probability_matrix[2:]
        negative_node2_cross_over_probability = negative_cross_over_probability_matrix[2:]
        print('Average PnL where the trades did not hit any node is:', cum_trade_pnl/(no_of_pos_crossover + no_of_neg_crossover))
        return positive_node2_cross_over_probability, negative_node2_cross_over_probability, cross_over_stock_prices

def generate_profit(cross_over_stock_prices, step_type, max_loss, max_qty, neg_crossover_prob, pos_crossover_prob):
    profits_array = []
    expected_prob_array = []
    cross_over_stock_prices = cross_over_stock_prices[cross_over_stock_prices['cross_over'] != 0].copy()
    for i in range(len(cross_over_stock_prices)):
        if step_type == 'ATR':
            step_size = cross_over_stock_prices.iloc[i]['atr'] / 2
        elif step_type == 'EWMA_VOL':
            step_size = cross_over_stock_prices.iloc[i]['ewma_vol_step']
        else:
            step_size = cross_over_stock_prices.iloc[i]['atr'] / 2
        binomial_tree = get_binomial_tree(cross_over_stock_prices.iloc[i]['close'], step_size)
        [u, u1, u0, u11, u00] = binomial_tree
        prices = [u, u1, u0, u11, u, u, u00]
        u11_ind, u10_ind, u01_ind, u00_ind = cross_over_stock_prices.iloc[i][['u11', 'u10', 'u01', 'u00']]
        if cross_over_stock_prices.iloc[i]['cross_over'] == 1:
            quantity, scenario_profits, exp = expectancy_maximise(pos_crossover_prob, prices, max_loss, max_qty)
            cross_over_stock_prices.at[cross_over_stock_prices.index[i], 'expected_profit'] = exp
            expected_prob_array.append(exp)
            scenario_profits = scenario_profits.astype(int)

        elif cross_over_stock_prices.iloc[i]['cross_over'] == -1:
            quantity, scenario_profits, exp = expectancy_maximise(neg_crossover_prob, prices, max_loss, max_qty)
            cross_over_stock_prices.at[cross_over_stock_prices.index[i],'expected_profit'] = exp
            expected_prob_array.append(exp)
            scenario_profits = scenario_profits.astype(int)
        if u11_ind:
            cross_over_stock_prices.at[cross_over_stock_prices.index[i],'trade_profit'] = scenario_profits[0]
            profits_array.append(scenario_profits[0])
        elif u10_ind:
            cross_over_stock_prices.at[cross_over_stock_prices.index[i],'trade_profit'] = scenario_profits[1]
            profits_array.append(scenario_profits[1])
        elif u01_ind:
            cross_over_stock_prices.at[cross_over_stock_prices.index[i],'trade_profit'] = scenario_profits[2]
            profits_array.append(scenario_profits[2])
        elif u00_ind:
            cross_over_stock_prices.at[cross_over_stock_prices.index[i],'trade_profit'] = scenario_profits[3]
            profits_array.append(scenario_profits[3])
    return profits_array, expected_prob_array, cross_over_stock_prices
def expectancy_maximise(crossover_prob, prices, max_loss, max_qty):
    qty = cp.Variable(7)
    profit_const = np.array([[1, 1, 0, 1, 0, 0, 0],
                             [1, 1, 0, 0, 1, 0, 0],
                             [1, 0, 1, 0, 0, 1, 0],
                             [1, 0, 1, 0, 0, 0, 1]])

    objective = cp.Minimize(cp.sum((crossover_prob.reshape(-1, 1) * profit_const * prices) @ qty))
    prob = cp.Problem(objective, [profit_const * prices @ qty <= max_loss, profit_const @ qty == 0, qty >= -max_qty,
                                  qty <= max_qty])

    prob.solve(solver=cp.CVXOPT, verbose=False)
    oqty = qty.value * -1
    expectancy = prob.value * -1
    scenario_profits = (profit_const * prices) @ oqty
    return oqty, scenario_profits, expectancy

