import pymdicator.timeseries as ts
from pymdicator.indicators import Momentum, MACD, RSI
import numpy as np
import datetime
import pytest
import os
from pandas import read_csv


@pytest.fixture(params=[False, True])
def test_data(request, datadir):
    if request.param:
        pd = read_csv(datadir.join('stock_data.txt'))
        dts = pd['Date'].tolist()
        vals = pd["Close"].tolist()
    else:
        dts = [datetime.date(2018, 1, 1)]
        for ii in range(1, 20):
            dts.append(dts[0] + datetime.timedelta(ii))
        vals = [100.0, 102.0, 99.0, 101.0, 103.0, 101.5, 103.0, 104.0, 103.5, 105,
                106.0, 105.5, 108.0, 109.0, 111.0, 109.5, 112.0, 114.0, 113.5, 115]
        pd = None
    test_ts = ts.Timeseries(dts, vals, ts.TimeseriesType.PRICE, ts.TimeseriesSubType.ABSOLUTE, 1)
    return {
        'dts': dts,
        'vals': vals,
        'test_ts': test_ts,
        'is_csv': request.param,
        'pd' : pd}


@pytest.fixture
def dts(test_data):
    return test_data['dts']


@pytest.fixture
def vals(test_data):
    return test_data['vals']


@pytest.fixture
def test_ts(test_data):
    return test_data['test_ts']


@pytest.fixture
def is_csv(test_data):
    return test_data['is_csv']


@pytest.fixture
def pd(test_data):
    return test_data['pd']


def test_latest_momentum(test_ts, vals, dts, is_csv, pd):
    momIndicator = Momentum(12)
    mom = momIndicator.calculate_current_ts(test_ts)

    if not is_csv:
        assert np.isclose(mom, 100.0 * 115.0 / 104.0)
    else:
        assert np.isclose(mom, 100.0*vals[-1] / vals[-13])
        mom = momIndicator.calculate_current_df(pd)
        assert np.isclose(mom, 100.0 * vals[-1] / vals[-13])


def test_latest_momentum_overlong(test_ts, vals):
    momIndicator = Momentum(len(test_ts))
    mom = momIndicator.calculate_current_ts(test_ts)
    assert np.isnan(mom)

    momIndicator = Momentum(len(test_ts) - 1)
    mom = momIndicator.calculate_current_ts(test_ts)
    assert np.isclose(mom, 100.0 * vals[-1] / vals[0])


def test_momentum_timeseries(test_ts, vals, dts, is_csv, pd):
    momIndicator = Momentum(10)
    mom_ts = momIndicator.calculate_timeseries_ts(test_ts)
    if not is_csv:
        assert np.isclose(mom_ts.values[0], 106.0)
        assert np.isclose(mom_ts.values[1], 105.5/1.02)
        assert np.isclose(mom_ts.values[2], 108.0/0.99)
        assert np.isclose(mom_ts.values[3], 109.0/1.01)
    else:
        n_checks = min(20, len(vals)-10)
        mom_ts_pd = momIndicator.calculate_timeseries_df(pd)
        for ii in range(n_checks):
            assert np.isclose(mom_ts.values[ii], 
                              100.0 * vals[ii + 10] / vals[ii])
            assert np.isclose(mom_ts_pd.values[ii], 
                              100.0 * vals[ii + 10] / vals[ii])


def test_latest_momentum_outer(test_ts, vals, dts, is_csv, pd):
    momIndicator = Momentum(12)
    mom = momIndicator.calculate_current(test_ts)

    if not is_csv:
        assert np.isclose(mom, 100.0 * 115.0 / 104.0)
    else:
        assert np.isclose(mom, 100.0*vals[-1] / vals[-13])
        mom_pd = momIndicator.calculate_current(pd)
        assert np.isclose(mom_pd, 100.0*vals[-1] / vals[-13])
        mom_dict = momIndicator.calculate_current({"a": pd})
        assert np.isclose(mom_dict["a"], 100.0*vals[-1] / vals[-13])


def test_momentum_timeseries_outer(test_ts, vals, dts, is_csv, pd):
    momIndicator = Momentum(10)
    mom_ts = momIndicator.calculate_timeseries(test_ts)
    if not is_csv:
        assert np.isclose(mom_ts.values[0], 106.0)
        assert np.isclose(mom_ts.values[1], 105.5/1.02)
        assert np.isclose(mom_ts.values[2], 108.0/0.99)
        assert np.isclose(mom_ts.values[3], 109.0/1.01)
    else:
        n_checks = min(20, len(vals)-10)
        mom_pd = momIndicator.calculate_timeseries(pd)
        mom_dict = momIndicator.calculate_timeseries({"a": pd})

        for ii in range(n_checks):
            assert np.isclose(mom_ts.values[ii], 
                              100.0 * vals[ii + 10] / vals[ii])
            assert np.isclose(mom_pd.values[ii], 
                              100.0 * vals[ii + 10] / vals[ii])
            assert np.isclose(mom_dict["a"].values[ii], 
                              100.0 * vals[ii + 10] / vals[ii])


def test_latest_macd(test_ts, vals, is_csv, pd):
    macd_calc = MACD()
    (macd, signal) = macd_calc.calculate_current_ts(test_ts)
    if not is_csv:
        assert np.isnan(macd) and np.isnan(signal)
    else:
        # I can't be bothered to do full calculation,
        # so make sure the values are sensible
        slow_average = sum(vals[-26:]) / 26.0
        fast_average = sum(vals[-12:]) / 12.0
        assert abs(macd) <= abs(2*(fast_average - slow_average))
        assert abs(signal) <= abs(2*(fast_average - slow_average))
        (macd_df, signal_df) = macd_calc.calculate_current_df(pd)
        assert np.isclose(macd_df, macd)
        assert np.isclose(signal_df, signal)


def test_latest_macd_outer(test_ts, vals, is_csv, pd):
    macd_calc = MACD()
    (macd, signal) = macd_calc.calculate_current(test_ts)
    if not is_csv:
        assert np.isnan(macd) and np.isnan(signal)
    else:
        # I can't be bothered to do full calculation,
        # so make sure the values are sensible
        slow_average = sum(vals[-26:]) / 26.0
        fast_average = sum(vals[-12:]) / 12.0
        assert abs(macd) <= abs(2*(fast_average - slow_average))
        assert abs(signal) <= abs(2*(fast_average - slow_average))
        (macd_df, signal_df) = macd_calc.calculate_current(pd)
        assert np.isclose(macd_df, macd)
        assert np.isclose(signal_df, signal)
        (macd_dict, signal_dict) = macd_calc.calculate_current({"a":pd})["a"]
        assert np.isclose(macd_dict, macd)
        assert np.isclose(signal_dict, signal)


def test_latest_rsi(test_ts, vals, is_csv, pd):
    rsi_calc = RSI(10)
    rsi = rsi_calc.calculate_current_ts(test_ts)
    if not is_csv:
        assert np.isclose(100.0 - 100.0 / (1 + 12.5/2.5), rsi)
    else:
        rsi_df = rsi_calc.calculate_current_df(pd)
        assert np.isclose(rsi, rsi_df)

def test_timeseries_rsi(test_ts, vals, is_csv, pd):
    rsi_calc = RSI(10)
    rsi = rsi_calc.calculate_current_ts(test_ts)
    rsi_ts = rsi_calc.calculate_timeseries_ts(test_ts)
    if not is_csv:
        assert np.isclose(100.0 - 100.0 / (1 + 12.5/2.5), rsi_ts.values[-1])
        assert np.isclose(100.0 - 100.0 / (1 + 12.5/2.5), rsi_ts.values[-2])
        assert np.isclose(100.0 - 100.0 / (1 + 12.5/2.5), rsi_ts.values[-3])
        assert np.isclose(100.0 - 100.0 / (1 + 11.5/2.5), rsi_ts.values[-4])
        assert np.isclose(100.0 - 100.0 / (1 + 10.5/2.5), rsi_ts.values[-5])
        assert np.isclose(100.0 - 100.0 / (1 + 10.5/2.5), rsi_ts.values[-6])
    else:
        assert np.isclose(rsi_ts.values[-1], rsi)