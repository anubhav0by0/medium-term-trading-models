import os.path
import sys, time
import numpy as np

from utils.datareader import DataClass
stock_data_folder = '..//NSE Data'
reader = DataClass(stock_data_folder)
start_time = time.time()
reader.delete_files_by_pattern()
combined_df = reader.get_all_files_name()
combined_df.to_csv('all_files.csv', index='False')
end_time = time.time()
# print('Time taken to read all the data file in NSE Data', np.round((end_time-start_time)/60,1))
# print(combined_df)