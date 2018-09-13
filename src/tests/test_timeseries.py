import teammagicsupergoal.timeseries as ts
import datetime
import numpy as np
import pytest


@pytest.fixture
def test_data():
    dts = [datetime.date(2018, 1, 1)]
    for ii in range(1, 10):
        dts.append(dts[0] + datetime.timedelta(ii))
    vals = [100.0, 102.0, 99.0, 101.0, 103.0, 101.5, 103.0, 104.0, 103.5, 105]
    test_dts = ts.Timeseries(dts, vals, ts.TimeseriesType.PRICE, ts.TimeseriesSubType.ABSOLUTE, 1)
    return {
        'dts': dts,
        'vals': vals,
        'test_ts': test_dts}


@pytest.fixture
def dts(test_data):
    return test_data['dts']


@pytest.fixture
def vals(test_data):
    return test_data['vals']


@pytest.fixture
def test_ts(test_data):
    return test_data['test_ts']


def test_len(test_ts):
    assert len(test_ts) == 10


def test_returns_absolute(test_ts, vals, dts):
    returns_ts = test_ts.calculate_returns(ts.TimeseriesSubType.ABSOLUTE, 1)
    assert len(returns_ts) == len(test_ts) - 1
    for ii in range(9):
        assert np.isclose(returns_ts.values[ii], vals[ii + 1] - vals[ii])
        assert returns_ts.dates[ii] == dts[ii]
    latest = test_ts.calculate_latest_return(ts.TimeseriesSubType.ABSOLUTE, 1)
    assert np.isclose(latest, returns_ts.values[-1])


def test_returns_fractional(test_ts, vals, dts):
    returns_ts = test_ts.calculate_returns(ts.TimeseriesSubType.FRACTIONAL, 2)
    assert len(returns_ts) == len(test_ts) - 2
    for ii in range(8):
        assert np.isclose(returns_ts.values[ii], vals[ii + 2] / vals[ii])
        assert returns_ts.dates[ii] == dts[ii]
    latest = test_ts.calculate_latest_return(ts.TimeseriesSubType.FRACTIONAL, 2)
    assert np.isclose(latest, returns_ts.values[-1])


def test_returns_log(test_ts, vals, dts):
    returns_ts = test_ts.calculate_returns(ts.TimeseriesSubType.LOG, 3)
    assert len(returns_ts) == len(test_ts) - 3
    for ii in range(7):
        assert np.isclose(returns_ts.values[ii], np.log(vals[ii + 3] / vals[ii]))
        assert returns_ts.dates[ii] == dts[ii]
    latest = test_ts.calculate_latest_return(ts.TimeseriesSubType.LOG, 3)
    assert np.isclose(latest, returns_ts.values[-1])


def test_moving_av_equal(test_ts, vals):
    av_ts = test_ts.calculate_moving_average(ts.TimeseriesSubType.EQUAL, 4)
    assert len(av_ts) == len(test_ts) - 3
    for ii in range(len(test_ts) - 4):
        assert np.isclose(av_ts.values[ii],
                          (vals[ii + 0] + vals[ii + 1] + vals[ii + 2] + vals[ii + 3])/4.0)


def test_single_moving_av_equal(test_ts, vals):
    av_ts = test_ts.calculate_moving_average(ts.TimeseriesSubType.EQUAL, 5)
    for ii in range(len(test_ts) - 5):
        assert np.isclose(av_ts.values[ii],
                          test_ts.calculate_single_moving_average(ts.TimeseriesSubType.EQUAL, 5, ii + 4))
        assert np.isclose(av_ts.values[-ii - 1],
                          test_ts.calculate_single_moving_average(ts.TimeseriesSubType.EQUAL, 5, -ii - 1))
    assert np.isclose(av_ts.values[-1],
                      test_ts.calculate_single_moving_average(ts.TimeseriesSubType.EQUAL, 5))


def test_single_moving_av_exp(test_ts, vals):
    test_val = (vals[-1]/2.0 + vals[-2]/4.0 + vals[-3]/8.0 + vals[-4]/16.0 + \
                vals[-5]/32.0 + vals[-6]/64.0 + vals[-7]/128.0 + vals[-8]/256.0) / (1 - 1/256.0)
    assert np.isclose(test_val,
                      test_ts.calculate_single_moving_average(ts.TimeseriesSubType.EXPONENTIAL, 3))
    assert np.isclose(test_val,
                      test_ts.calculate_single_moving_average(ts.TimeseriesSubType.EXPONENTIAL, 3, len(vals)-1))
    assert np.isclose(test_val,
                      test_ts.calculate_single_moving_average(ts.TimeseriesSubType.EXPONENTIAL, 3, -1))
    
    test_val = (vals[-3] + vals[-4]/3.0 + vals[-5]/9.0 + vals[-6]/27.0 + \
                vals[-7]/81.0 + vals[-8]/243.0) / (1 + 1.0/3 + 1.0/9 + 1.0/27 + 1.0/81 + 1.0/243)

    assert np.isclose(test_val,
                      test_ts.calculate_single_moving_average(ts.TimeseriesSubType.EXPONENTIAL, 2, len(vals)-3))
    assert np.isclose(test_val,
                      test_ts.calculate_single_moving_average(ts.TimeseriesSubType.EXPONENTIAL, 2, -3))


def test_moving_av_exp(test_ts, vals):
    av_ts = test_ts.calculate_moving_average(ts.TimeseriesSubType.EXPONENTIAL, 3)
    assert len(av_ts) == len(test_ts) - 2
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


def test_vol_equal(test_ts, vals):
    vol_ts = test_ts.calculate_volatility(ts.TimeseriesSubType.EQUAL, 4)
    vals2 = (np.array(vals) * np.array(vals)).tolist()
    av_ts = test_ts.calculate_moving_average(ts.TimeseriesSubType.EQUAL, 4)

    assert len(vol_ts) == len(test_ts) - 3
    for ii in range(7):
        assert np.isclose(vol_ts.values[ii], 
                          np.sqrt((vals2[ii] + vals2[ii+1] + vals2[ii+2] + vals2[ii+3])/4 -
                                   av_ts.values[ii]*av_ts.values[ii]))


def test_vol_exp(test_ts, vals):
    vol_ts = test_ts.calculate_volatility(ts.TimeseriesSubType.EXPONENTIAL, 3)
    vals2 = (np.array(vals) * np.array(vals)).tolist()
    av_ts = test_ts.calculate_moving_average(ts.TimeseriesSubType.EXPONENTIAL, 3)

    assert len(vol_ts) == len(test_ts) - 2
    assert np.isclose(vol_ts.values[0],
                      np.sqrt((vals2[0] + vals2[1] + vals2[2])/3 -
                              av_ts.values[0] * av_ts.values[0]))
    assert np.isclose(vol_ts.values[1],
                      np.sqrt((vals2[0] + vals2[1] + vals2[2])/6 + vals2[3]/2 -
                              av_ts.values[1] * av_ts.values[1]))
    assert np.isclose(vol_ts.values[2],
                      np.sqrt((vals2[0] + vals2[1] + vals2[2])/12 + vals2[3]/4  + vals2[4]/2 -
                              av_ts.values[2] * av_ts.values[2]))
    assert np.isclose(vol_ts.values[3],
                      np.sqrt((vals2[0] + vals2[1] + vals2[2])/24 + vals2[3]/8  + 
                              vals2[4]/4 + vals2[5]/2 -
                              av_ts.values[3] * av_ts.values[3]))
    assert np.isclose(vol_ts.values[4],
                      np.sqrt((vals2[0] + vals2[1] + vals2[2])/48 + vals2[3]/16  + 
                              vals2[4]/8 + vals2[5]/4 + vals2[6]/2 -
                              av_ts.values[4] * av_ts.values[4]))
