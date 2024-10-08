import pandas as pd

def read_input_data(file_path):
    """
    Reads a csv file which is in the format provided
    :returns: Dataframe
    """
    ticker_data = pd.read_csv(file_path).iloc[:,1:]
    ticker_data.set_index(pd.to_datetime(ticker_data['date'], format='%d-%m-%y %H:%M'), inplace=True, drop=True)
    ticker_data = ticker_data.iloc[::-1]
    return ticker_data
class DataClass:
    def __init__(self, data_folder):
        self.data_folder = data_folder