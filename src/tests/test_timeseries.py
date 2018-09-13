import teammagicsupergoal.timeseries as ts
import datetime
import numpy as np

dts = [datetime.date(2018,1,1)]
for ii in range(1,10) :
    dts.append(dts[0] + datetime.timedelta(ii))

vals = [100.0, 102.0, 99.0, 101.0, 103.0, 101.5, 103.0, 104.0, 103.5, 105]

test_ts = ts.Timeseries(dts, vals, ts.TimeseriesType.PRICE, ts.TimeseriesSubType.ABSOLUTE, 1)

def test_returns_absolute():
    returns_ts = test_ts.calculate_returns(ts.TimeseriesSubType.ABSOLUTE, 1)
    assert len(returns_ts.dates) == len(test_ts.dates) - 1
    for ii in range(9):
        assert np.isclose(returns_ts.values[ii], vals[ii + 1] - vals[ii])
        assert returns_ts.dates[ii] == dts[ii]

def test_returns_fractional():
    returns_ts = test_ts.calculate_returns(ts.TimeseriesSubType.FRACTIONAL, 2)
    assert len(returns_ts.dates) == len(test_ts.dates) - 2
    for ii in range(8):
        assert np.isclose(returns_ts.values[ii], vals[ii + 2] / vals[ii])
        assert returns_ts.dates[ii] == dts[ii]

def test_returns_log():
    returns_ts = test_ts.calculate_returns(ts.TimeseriesSubType.LOG, 3)
    assert len(returns_ts.dates) == len(test_ts.dates) - 3
    for ii in range(7):
        assert np.isclose(returns_ts.values[ii], np.log(vals[ii + 3] / vals[ii]))
        assert returns_ts.dates[ii] == dts[ii]

def test_moving_av_equal():
    av_ts = test_ts.calculate_moving_average(ts.TimeseriesSubType.EQUAL, 4)
    assert len(av_ts.dates) == len(test_ts.dates) - 3
    for ii in range(7):
        assert np.isclose(av_ts.values[ii], 
                          (vals[ii + 0] + vals[ii + 1] + vals[ii + 2] + vals[ii + 3])/4.0)

def test_moving_av_exp():
    av_ts = test_ts.calculate_moving_average(ts.TimeseriesSubType.EXPONENTIAL, 3)
    assert len(av_ts.dates) == len(test_ts.dates) - 2
    assert np.isclose(av_ts.values[0],
                      (vals[0] + vals[1] + vals[2])/3.0)
    assert np.isclose(av_ts.values[1],
                      (vals[0] + vals[1] + vals[2])/6.0 + vals[3]/2.0)
    assert np.isclose(av_ts.values[2],
                      (vals[0] + vals[1] + vals[2])/12.0 + vals[3]/4.0 + vals[4]/2.0)
    assert np.isclose(av_ts.values[3],
                      (vals[0] + vals[1] + vals[2])/24.0 + vals[3]/8.0 + \
                      vals[4]/4.0 + vals[5]/2.0)
    assert np.isclose(av_ts.values[4],
                      (vals[0] + vals[1] + vals[2])/48.0 + vals[3]/16.0 + \
                      vals[4]/8.0 + vals[5]/4.0 + vals[6]/2.0)
