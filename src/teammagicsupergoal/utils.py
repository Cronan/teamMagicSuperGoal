import os
from pandas import read_csv

this_dir, this_filename = os.path.split(__file__)


STOCKS = 'Stocks'
ETFS = 'ETFs'

PATHS = {
    STOCKS: os.path.join(this_dir, "data", 'Stocks'),
    ETFS: os.path.join(this_dir, "data", "ETFs"),
}


def list_files(path):
    return os.listdir(path)


def read_csv_to_df(path):
    return read_csv(path)
