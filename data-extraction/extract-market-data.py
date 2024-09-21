import pandas as pd
import os
from concurrent.futures import ThreadPoolExecutor

def read_parquet_files(filepath):
    """Reads a single parquet file, adds a column to the dataframe with column name as ticker_name
    whose value is the filename. If the volume is less than 1000 at any given point in time,
    then we do not consider the stock
     and returns a dataframe"""
    stock_data = pd.DataFrame()
    required_columns = ['date', 'open', 'high', 'low', 'close', 'volume', 'ticker_name']
    try:
        stock_data = pd.read_parquet(filepath)
        ticker_name = filepath.split('\\')[-1].split('.')[0]
        stock_data['ticker_name'] = ticker_name
        # print(stock_data)
        if not set(required_columns).issubset(stock_data.columns):
            return pd.DataFrame()
        if(stock_data['volume']< 1000).any():
            stock_data= pd.DataFrame()
        # print(stock_data)
    except Exception as ex:
        print(ex)
    return stock_data

def read_input_data(data_folder):
    """Obtains a folder path and reads through all the parquet files in the same.
    The final output is a dataframe which consists of the ticker name and OLHC data"""
    all_files = [os.path.join(data_folder, file) for file in os.listdir(stock_data_folder)]
    # Use of Threadpool Executor to read through all the files in parallel utilizing multiple Threads
    with ThreadPoolExecutor(max_workers=15) as executor:
        dataframes = list(executor.map(read_parquet_files, all_files))
    # Concatenate all Dataframes into one large Dataframes
    consolidated_df = pd.concat(dataframes, ignore_index=True)
    return consolidated_df

# print(pd.read_parquet(path='..//input//0IHFL26-YR.parquet'))
stock_data_folder = '..//..//NSE Data'
combined_df = read_input_data(stock_data_folder)