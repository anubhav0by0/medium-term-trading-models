import pandas as pd
import os, re
from concurrent.futures import ThreadPoolExecutor


def _read_parquet_file(filepath):
    """Reads a single parquet file, adds a column to the dataframe with column name as ticker_name
    whose value is the filename. If the volume is less than 1000 at any given point in time,
    then we do not consider the stock
     and returns a dataframe"""
    stock_data = pd.DataFrame()
    required_columns = ['date', 'open', 'high', 'low', 'close', 'volume', 'ticker_name']
    ticker_name = filepath.split('\\')[-1].split('.')[0]
    # print(filepath)
    try:
        stock_data = pd.read_parquet(filepath, engine='pyarrow')
        stock_data['ticker_name'] = ticker_name
        # print(stock_data)
        if not set(required_columns).issubset(stock_data.columns):
            return pd.DataFrame()

    except Exception as ex:
        print(ticker_name, ex)
    return stock_data


class DataClass:
    def __init__(self, data_folder):
        self.data_folder = data_folder

    def read_input_data(self):
        """Obtains a folder path and reads through all the parquet files in the same.
        The final output is a dataframe which consists of the ticker name and OLHC data"""
        data_folder = self.data_folder
        all_files = [os.path.join(data_folder, file) for file in os.listdir(data_folder)]
        # Use of ThreadPool Executor to read through all the files in parallel utilizing multiple Threads
        with ThreadPoolExecutor(max_workers=15) as executor:
            dataframes = list(executor.map(_read_parquet_file, all_files))
        # Concatenate all Dataframes into one large Dataframes
        consolidated_df = pd.concat(dataframes, ignore_index=True)
        return consolidated_df

    def get_all_files_name(self):
        data_folder = self.data_folder
        all_files = [file.split('.')[0] for file in os.listdir(data_folder)]
        return pd.DataFrame(all_files, columns=['File Name'])


    def delete_files_by_pattern(self):
        folder_path = self.data_folder
        # Define regex patterns to match the required file names
        patterns = [
            r'-[NYZP][0-9]$',  # Matches -N, -Y, -Z followed by a digit 0-9 (no files will have -10 as per instruction)
            r'-[NYZ][A-Z]$',  # Matches -N followed by a single letter A-Z
            r'-(GS|SG|TB|GS|D1|GB|IV|BZ)$',
            r'ETF', r'CASE', r'BEES'
        ]

        # Compile the patterns into a single regex for performance
        combined_pattern = re.compile('|'.join(patterns))

        # Iterate through files in the folder
        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)
            file_name = file_name.split('.')[0]
            # Check if it's a file and matches any of the patterns
            if os.path.isfile(file_path) and combined_pattern.search(file_name):
                print(f"Deleting file: {file_path}")
                os.remove(file_path)  # Delete the file



