from pandas import read_csv


def test_read_csv(datadir):
    df = read_csv(datadir.join('stock_data.txt'))
    assert df is not None
    assert 4521 == len(df)
