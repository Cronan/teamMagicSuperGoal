import teammagicsupergoal.timeseries as ts
from teammagicsupergoal.indicators import Momentum
import numpy as np
import datetime
import pytest
from teammagicsupergoal.utils import read_csv_to_df, PATHS, STOCKS
import os


@pytest.fixture(params=[False, pytest.mark.skipif('TEAM_MAGIC_SKIP_DATA' in os.environ, reason="reason")(True)])
def test_data(request):
    if request.param:
        pd = read_csv_to_df(os.path.join(PATHS[STOCKS], 'a.us.txt'))
        dts = pd['Date'].tolist()
        vals = pd["Close"].tolist()
    else:
        dts = [datetime.date(2018, 1, 1)]
        for ii in range(1, 20):
            dts.append(dts[0] + datetime.timedelta(ii))
        vals = [100.0, 102.0, 99.0, 101.0, 103.0, 101.5, 103.0, 104.0, 103.5, 105,
                106.0, 105.5, 108.0, 109.0, 111.0, 109.5, 112.0, 114.0, 113.5, 115]
    test_ts = ts.Timeseries(dts, vals, ts.TimeseriesType.PRICE, ts.TimeseriesSubType.ABSOLUTE, 1)
    return {
        'dts': dts,
        'vals': vals,
        'test_ts': test_ts,
        'is_csv': request.param}


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


def test_latest_momentum(test_ts, vals, dts, is_csv):
    momIndicator = Momentum(12)
    mom = momIndicator.calculate_current_ts(test_ts)

    if not is_csv:
        assert np.isclose(mom, 100.0 * 115.0 / 104.0)
    else:
        assert np.isclose(mom, 100.0 * vals[-1] / vals[-13])


def test_latest_momentum_overlong(test_ts, vals):
    momIndicator = Momentum(len(test_ts))
    mom = momIndicator.calculate_current_ts(test_ts)
    assert np.isnan(mom)

    momIndicator = Momentum(len(test_ts) - 1)
    mom = momIndicator.calculate_current_ts(test_ts)
    assert np.isclose(mom, 100.0 * vals[-1] / vals[0])


def test_momentum_timeseries(test_ts, vals, dts, is_csv):
    momIndicator = Momentum(10)
    mom_ts = momIndicator.calculate_timeseries_ts(test_ts)
    if not is_csv:
        assert np.isclose(mom_ts.values[0], 106.0)
        assert np.isclose(mom_ts.values[1], 105.5/1.02)
        assert np.isclose(mom_ts.values[2], 108.0/0.99)
        assert np.isclose(mom_ts.values[3], 109.0/1.01)
    else:
        n_checks = min(20, len(vals)-10)
        for ii in range(n_checks):
            assert np.isclose(mom_ts.values[ii], 
                              100.0 * vals[ii + 10] / vals[ii])


def test_latest_momentum_outer(test_ts, vals, dts, is_csv):
    momIndicator = Momentum(12)
    mom = momIndicator.calculate_current(test_ts)

    if not is_csv:
        assert np.isclose(mom, 100.0 * 115.0 / 104.0)
    else:
        assert np.isclose(mom, 100.0*vals[-1] / vals[-13])


def test_momentum_timeseries_outer(test_ts, vals, dts, is_csv):
    momIndicator = Momentum(10)
    mom_ts = momIndicator.calculate_timeseries(test_ts)
    if not is_csv:
        assert np.isclose(mom_ts.values[0], 106.0)
        assert np.isclose(mom_ts.values[1], 105.5/1.02)
        assert np.isclose(mom_ts.values[2], 108.0/0.99)
        assert np.isclose(mom_ts.values[3], 109.0/1.01)
    else:
        n_checks = min(20, len(vals)-10)
        for ii in range(n_checks):
            assert np.isclose(mom_ts.values[ii], 
                              100.0 * vals[ii + 10] / vals[ii])
