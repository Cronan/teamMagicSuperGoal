from teammagicsupergoal.utils import PATHS, STOCKS, ETFS
from teammagicsupergoal.utils import list_files, read_csv_to_df
import os
import time


def test_etf_list():
    assert 1300 < len(list_files(PATHS[ETFS]))


def test_stock_list():
    assert 1300 < len(list_files(PATHS[STOCKS]))


def test_read_csv():
    df = read_csv_to_df(os.path.join(PATHS[STOCKS], 'a.us.txt'))
    assert df is not None
    assert 4521 == len(df)


def test_random_100_stocks_load():
    from pandas.io.common import EmptyDataError
    import random
    t0 = time.time()
    stocks = list_files(PATHS[STOCKS])
    n = len(stocks)
    l = 100
    start = random.randint(0, n-l)
    for file_name in stocks[start:start + l]:
        try:
            file_path = os.path.join(PATHS[STOCKS], file_name)
            df = read_csv_to_df(file_path)
            assert 0 < len(df)
        except EmptyDataError:
            continue
        except:
            print(file_path)
            raise
        assert df is not None
        assert 0 < len(df)
    t1 = time.time()
    assert 5 > t1 - t0
