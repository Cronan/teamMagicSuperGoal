from teammagicsupergoal.utils import PATHS, STOCKS, ETFS
from teammagicsupergoal.utils import list_files, read_csv_to_df
import os
import time
import pytest


@pytest.fixture
def etfs():
    return list_files(PATHS[ETFS])


@pytest.fixture
def stocks():
    return list_files(PATHS[STOCKS])


@pytest.mark.skipif('TEAM_MAGIC_SKIP_DATA' in os.environ, reason="No data")
def test_etf_list(etfs):
    assert 1300 < len(etfs)
    assert 'aadr.us.txt' == etfs[0]


@pytest.mark.skipif('TEAM_MAGIC_SKIP_DATA' in os.environ, reason="No data")
def test_stock_list(stocks):
    assert 1300 < len(stocks)
    assert 'a.us.txt' == stocks[0]


@pytest.mark.skipif('TEAM_MAGIC_SKIP_DATA' in os.environ, reason="No data")
def test_read_csv():
    df = read_csv_to_df(os.path.join(PATHS[STOCKS], 'a.us.txt'))
    assert df is not None
    assert 4521 == len(df)


@pytest.mark.skipif('TEAM_MAGIC_SKIP_DATA' in os.environ, reason="No data")
def test_random_100_stocks_load(stocks):
    import random
    t0 = time.time()
    n = len(stocks)
    l = 100
    start = random.randint(0, n-l)
    for file_name in stocks[start:start + l]:
        df = read_csv_to_df(os.path.join(PATHS[STOCKS], file_name))
        if df is not None:
            assert 0 < len(df)
    t1 = time.time()
    assert 5 > t1 - t0
