from teammagicsupergoal.timeseries import Timeseries, TimeseriesType, TimeseriesSubType
import numpy as np
import pandas

DATE_COL_NAME = "Date"
PRICE_COL_NAME = "Close"

class TechnicalIndicator:
    MOMENTUM = "Momentum"
    RSI = "Relative Strength Indicator"
    MACD = "Moving Average Convergence Divergence"

    def __init__(self, indicator_name):
        self.name = indicator_name

    def calculate_current(self, *parameter_list):
        data = parameter_list[0]
        other_args = parameter_list[1:] if len(parameter_list) > 1 else []

        if isinstance(data, Timeseries):
            return self.calculate_current_ts(data, *other_args)
        elif isinstance(data, pandas.DataFrame):
            return self.calculate_current_df(data, *other_args)
        elif isinstance(data, dict):
            return self.calculate_current_all(data, *other_args)
        return None

    def calculate_timeseries(self, *parameter_list):
        data = parameter_list[0]
        other_args = parameter_list[1:] if len(parameter_list) > 1 else []

        if isinstance(data, Timeseries):
            return self.calculate_timeseries_ts(data, *other_args)
        elif isinstance(data, pandas.DataFrame):
            return self.calculate_timeseries_df(data, *other_args)
        elif isinstance(data, dict):
            return self.calculate_timeseries_all(data, *other_args)
        return None

    def calculate_current_ts(self, ts, *parameter_list):
        raise NotImplementedError

    def calculate_timeseries_ts(self, ts, *parameter_list):
        raise NotImplementedError

    def calculate_current_df(self, df, *parameter_list):
        raise NotImplementedError

    def calculate_timeseries_df(self, df, *parameter_list):
        raise NotImplementedError

    def calculate_current_all(self, df_dictionary, *parameter_list):
        results = {}
        for security in df_dictionary:
            if df_dictionary[security] is not None:
                results[security] = self.calculate_current_df(df_dictionary[security],
                                                              *parameter_list)
            else:
                results[security] = None
        return results

    def calculate_timeseries_all(self, df_dictionary, *parameter_list):
        results = {}
        for security in df_dictionary:
            if df_dictionary[security] is not None:
                results[security] = self.calculate_timeseries_df(df_dictionary[security],
                                                                 *parameter_list)
            else:
                results[security] = None
        return results


class Momentum(TechnicalIndicator):
    def __init__(self, n_days):
        TechnicalIndicator.__init__(self, TechnicalIndicator.MOMENTUM)
        self.n_days = n_days
    
    def calculate_current_ts(self, ts):
        '''
        Calculate the price momentum for the provided time-series
        '''
        if ts.ts_type == TimeseriesType.PRICE:
            return 100 * ts.calculate_latest_return(TimeseriesSubType.FRACTIONAL, self.n_days)
        elif ts.ts_type == TimeseriesType.RETURNS and \
          ts.ts_sub_type == TimeseriesSubType.FRACTIONAL and \
          ts.period == self.n_days:
            return 100 * ts.values[-1]
        elif ts.ts_type == TimeseriesType.RETURNS and \
          ts.ts_sub_type == TimeseriesSubType.LOG and \
          ts.period == self.n_days:
            return 100 * np.exp(ts.values[-1])
        
        return None
    
    def calculate_timeseries_ts(self, ts):
        '''
        Calculate the price momentum for the provided time-series
        '''
        mom = None
        if ts.ts_type == TimeseriesType.PRICE:
            mom = ts.calculate_returns(TimeseriesSubType.FRACTIONAL, \
                                       self.n_days).linear_transform(100.0, 0)
        elif ts.ts_type == TimeseriesType.RETURNS and \
          ts.ts_sub_type == TimeseriesSubType.FRACTIONAL and \
          ts.period == self.n_days:
            mom = ts.linear_transform(100.0, 0)
        elif ts.ts_type == TimeseriesType.RETURNS and \
          ts.ts_sub_type == TimeseriesSubType.LOG and \
          ts.period == self.n_days:
            mom = ts.transform_log_to_fractional_returns().linear_transform(100.0, 0)
        
        if mom != None:
            mom.set_indicator_type(TechnicalIndicator.MOMENTUM)

        return mom

    def calculate_current_df(self, df, date_col_name = DATE_COL_NAME,
                          price_col_name = PRICE_COL_NAME):
        dates = df[date_col_name].tolist()
        prices = df[price_col_name].tolist()

        ts = Timeseries(dates, prices, TimeseriesType.PRICE, TimeseriesSubType.ABSOLUTE)
        return self.calculate_current_ts(ts)

    def calculate_timeseries_df(self, df, date_col_name = DATE_COL_NAME,
                                price_col_name = PRICE_COL_NAME):
        dates = df[date_col_name].tolist()
        prices = df[price_col_name].tolist()

        ts = Timeseries(dates, prices, TimeseriesType.PRICE, TimeseriesSubType.ABSOLUTE)
        return self.calculate_timeseries_ts(ts)


class MACD(TechnicalIndicator):
    def __init__(self, short_days = 12, long_days = 26, signal_days = 9):
        TechnicalIndicator.__init__(self, TechnicalIndicator.MACD)
        assert short_days < long_days
        self.long_days = long_days
        self.short_days = short_days
        self.signal_days = signal_days

    def calculate_current_ts(self, ts):
        fast = ts.calculate_moving_average_truncate(TimeseriesSubType.EXPONENTIAL,
                                                    self.short_days, -self.signal_days)
        slow = ts.calculate_moving_average_truncate(TimeseriesSubType.EXPONENTIAL,
                                                    self.long_days, -self.signal_days)
        macd = Timeseries.linearly_combine(fast, 1.0, slow, -1.0)
        signal = macd.calculate_single_moving_average(TimeseriesSubType.EXPONENTIAL,
                                                      self.signal_days)
        return (macd.values[-1], signal)

    def calculate_timeseries_ts(self, ts):
        fast = ts.calculate_moving_average(TimeseriesSubType.EXPONENTIAL,
                                           self.short_days)
        slow = ts.calculate_moving_average(TimeseriesSubType.EXPONENTIAL,
                                           self.long_days)
        macd = Timeseries.linearly_combine(fast, 1.0, slow, -1.0)
        signal = macd.calculate_moving_average(TimeseriesSubType.EXPONENTIAL,
                                               self.signal_days)
        macd = macd.create_truncate(len(signal))
        return (macd, signal)

    def calculate_current_df(self, df, date_col_name = DATE_COL_NAME,
                             price_col_name = PRICE_COL_NAME):
        dates = df[date_col_name].tolist()
        prices = df[price_col_name].tolist()

        ts = Timeseries(dates, prices, TimeseriesType.PRICE, TimeseriesSubType.ABSOLUTE)
        return self.calculate_current_ts(ts)

    def calculate_timeseries_df(self, df, date_col_name = DATE_COL_NAME,
                                price_col_name = PRICE_COL_NAME):
        dates = df[date_col_name].tolist()
        prices = df[price_col_name].tolist()

        ts = Timeseries(dates, prices, TimeseriesType.PRICE, TimeseriesSubType.ABSOLUTE)
        return self.calculate_timeseries_ts(ts)
