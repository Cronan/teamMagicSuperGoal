import timeseries
import datetime
import numpy as np

dts = [datetime.date(2018,1,1)]
for ii in range(1,10) :
    dts.append(dts[0] + datetime.timedelta(ii))

vals = [100.0, 102.0, 99.0, 101.0, 103.0, \
        101.5, 103,0, 104.0, 103.5, 105]

test_ts = timeseries.Timeseries(dts, vals, timeseries.TimeseriesType.PRICE, timeseries.TimeseriesSubType.ABSOLUTE, 1)

def test_returns_absolute():
    returns_ts = test_ts.calculate_returns(timeseries.TimeseriesSubType.ABSOLUTE, 1)
    assert len(returns_ts.dates) == len(test_ts.dates - 1)
    for ii in range(9):
        assert np.isclose(returns_ts.values[ii], vals[ii + 1] - vals[ii])
        assert returns_ts.dates[ii] == dts[ii]

def test_returns_fractional():
    returns_ts = test_ts.calculate_returns(timeseries.TimeseriesSubType.FRACTIONAL, 2)
    assert len(returns_ts.dates) == len(test_ts.dates - 2)
    for ii in range(8):
        assert np.isclose(returns_ts.values[ii], vals[ii + 2] / vals[ii])
        assert returns_ts.dates[ii] == dts[ii]

def test_returns_log():
    returns_ts = test_ts.calculate_returns(timeseries.TimeseriesSubType.FRACTIONAL, 3)
    assert len(returns_ts.dates) == len(test_ts.dates - 3)
    for ii in range(7):
        assert np.isclose(returns_ts.values[ii], np.log( vals[ii + 3] / vals[ii]))
        assert returns_ts.dates[ii] == dts[ii]
