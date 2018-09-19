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
    files = os.listdir(path)
    files.sort()
    return files


def read_csv_to_df(path):
    from pandas.io.common import EmptyDataError
    try:
        return read_csv(path)
    except EmptyDataError:
        return None
    except:
        raise
