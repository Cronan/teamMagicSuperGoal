import pandas as pd
import numpy as np
import logging as log

class TimeseriesType:
    PRICE = "Price"
    RETURNS = "Returns"
    VOL = "Volatility"
    MOVING_AVERAGE = "Moving Average"
    INDICATOR = "Technical Indicator"

class TimeseriesSubType:
    NONE = "None"
    FRACTIONAL = "Fractional"
    LOG = "Logarithmic"
    ABSOLUTE = "Absolute"
    RELATIVE = "Relative"
    EXPONENTIAL = "Exponential"
    EQUAL = "Equal"

class Timeseries:
    def __init__(self, dates, values, tsType = None, tsSubType = None, period = None):
        '''
        Initialize timeseries object.
        Dates are assumed to be passed in in order.

        dates : list of dates
        values : list of values
        tsType : timeseries type
        tsSubType : timeseries subtype
        period : periodicity
        '''
        if len(dates) != len(values):
            log.error("Cannot create timeseries - mis-match in lengths")
            return None

        self.dates = dates
        self.values = values
        self.__np_values = np.array(values)
        index = pd.DatetimeIndex(dates)
        self.series = pd.Series(values, index = index)
        self.ts_type = tsType
        self.ts_sub_type = tsSubType
        self.period = period

    def calculate_returns(self, returns_type = TimeseriesSubType.FRACTIONAL, period = 1):
        '''
        Calculate a new time-series based on returns from this timeseries
        Returned time-series is indexed by starting day for each returns period.

        returns_type : Fractional/Logarithmic/Absolute
        period : number of days to calculate each return over
        '''
        new_dates = self.dates[0:-period]
        np_new_values = None
        if returns_type == TimeseriesSubType.FRACTIONAL:
            np_new_values = self.__np_values[period:] / self.__np_values[0:-period]
        elif returns_type == TimeseriesSubType.ABSOLUTE:
            np_new_values = self.__np_values[period:] - self.__np_values[0:-period]
        elif returns_type == TimeseriesSubType.LOG:
            np_new_values = np.log(self.__np_values[period:] / self.__np_values[0:-period])

        new_ts = Timeseries(new_dates, np_new_values.tolist(), TimeseriesType.RETURNS,
                            returns_type, period)
        return new_ts

    def calculate_latest_return(self, returns_type = TimeseriesSubType.FRACTIONAL, period = 1):
        '''
        Calculate the latest return.

        returns_type : Fractional/Logarithmic/Absolute
        period : number of days to calculate the return over
        '''
        if returns_type == TimeseriesSubType.FRACTIONAL:
            return self.__np_values[-1] / self.__np_values[-period-1]
        elif returns_type == TimeseriesSubType.ABSOLUTE:
            return self.__np_values[-1] - self.__np_values[-period-1]
        elif returns_type == TimeseriesSubType.LOG:
            return np.log(self.__np_values[-1] / self.__np_values[-period-1])

    def calculate_moving_average(self, weighting_type = TimeseriesSubType.EQUAL, period = 15):
        '''
        Calculate moving average for current time-series

        weighting_type : Exponential/Equal
        period : period for moving average calculation
        '''
        moving_average = None
        
        if weighting_type == TimeseriesSubType.EQUAL:
            np_sum = self.__np_values[period - 1:]
            for ii in range(1, period):
                np_sum = np_sum + self.__np_values[period - ii - 1: -ii]
            moving_average = (np_sum / period).tolist()
        elif weighting_type == TimeseriesSubType.EXPONENTIAL:
            moving_average = []
            alpha = 2.0 / (period + 1.0)
            moving_average.append(sum(self.__np_values[0:period]) / period)
            for val in self.values[period:]:
                new_av = val * alpha + moving_average[-1] * (1.0 - alpha)
                moving_average.append(new_av)
        
        new_ts = Timeseries(self.dates[period-1:], moving_average,
                            TimeseriesType.MOVING_AVERAGE, weighting_type, period)
        return new_ts

    def calculate_single_moving_average(self, weighting_type = TimeseriesSubType.EQUAL, period = 15, index = None):
        '''
        Calculate the latest moving average.  Where exponential weighting is used, calculation is
        truncated to point with weighting of 1/100th of latest point.

        weighting_type : Exponential/Equal
        period : period for moving average calculation

        '''
        if index == None:
            index = len(self) - 1
        if index < 0:
            index = len(self) + index
        if period > index + 1:
            period = index + 1

        if weighting_type == TimeseriesSubType.EQUAL:
            return sum(self.__np_values[index - period + 1:index + 1]) / period
        elif weighting_type == TimeseriesSubType.EXPONENTIAL:
            alpha = 2.0 / (period + 1.0)
            n_end = int(-2.0 / np.log10(1 - alpha) + 1)
            total = 0
            total_wgt = 0
            for val in self.values[max(index - n_end, 0):index + 1]:
                total = total * (1 - alpha) + val
                total_wgt = total_wgt * (1 - alpha) + 1

            return total / total_wgt
        assert False

    def calculate_moving_average_truncate(self, weighting_type = TimeseriesSubType.EQUAL, period = 15, start_idx = None):
        '''
        Calculate a moving average timeseries

        weighting_type : Equal/Exponential
        period : Period to use for calculation
        start_idx : Index to start calculation for
        '''
        if start_idx == None:
            start_idx = period - 1
        if period > start_idx + 1:
            start_idx = period - 1

        moving_average = None

        if weighting_type == TimeseriesSubType.EQUAL:
            np_sum = self.__np_values[start_idx:]
            for ii in range(1, period):
                np_sum = np_sum + self.__np_values[start_idx - ii: -ii]
            moving_average = (np_sum / period).tolist()
        elif weighting_type == TimeseriesSubType.EXPONENTIAL:
            moving_average = []
            moving_average.append(self.calculate_single_moving_average(weighting_type, period, start_idx))
            alpha = 2.0 / (period + 1.0)

            for val in self.values[start_idx + 1:]:
                new_av = val * alpha + moving_average[-1] * (1.0 - alpha)
                moving_average.append(new_av)

        new_ts = Timeseries(self.dates[start_idx:], moving_average,
                            TimeseriesType.MOVING_AVERAGE, weighting_type, period)
        return new_ts

    def calculate_volatility(self, weighting_type, period = 30, moving_average = None):
        '''
        Calculate a new time-series based on the volatility of this timeseries
        Returned time-series is indexed by last date in volatility period

        weighting_type : Exponential/Equal
        period : period for volatility calculation
        moving_average : Moving average time-series (if None then calculated on the fly)
        '''
        if moving_average is None:
            moving_average = self.calculate_moving_average(weighting_type, period)

        vals_sq = self.__np_values * self.__np_values

        if weighting_type == TimeseriesSubType.EQUAL:
            np_sum_sq = vals_sq[period - 1:]
            for ii in range(1, period):
                np_sum_sq = np_sum_sq + vals_sq[period - ii - 1: -ii]
            np_volatilities = np.sqrt((np_sum_sq / period) - \
                                   (moving_average.__np_values * moving_average.__np_values))
        elif weighting_type == TimeseriesSubType.EXPONENTIAL:
            sum_weighted_squares = []
            alpha = 2.0 / (period + 1.0)
            sum_weighted_squares.append(sum(self.__np_values[0:period] * \
                                        self.__np_values[0:period])/period)
            for val2 in vals_sq[period:]:
                new_val2 = val2 * alpha + sum_weighted_squares[-1] * (1.0 - alpha)
                sum_weighted_squares.append(new_val2)
            np_volatilities = np.sqrt(np.array(sum_weighted_squares) - \
                                      moving_average.__np_values * moving_average.__np_values)

        new_ts = Timeseries(self.dates[period-1:], np_volatilities.tolist(), \
                            TimeseriesType.VOL, weighting_type, period)

        return new_ts

    def __len__(self):
        return len(self.dates)

    def linear_transform(self, factor, shift):
        '''
        Apply a linear shift to timeseries <values> -> factor * <values> + shift
        factor : Scaling factor
        shift : shift
        '''
        new_vals = (self.__np_values * factor * 1.0 + shift * 1.0).tolist()
        return Timeseries(self.dates, new_vals, self.ts_type, self.ts_sub_type, self.period)

    def transform_log_to_fractional_returns(self):        
        '''
        Convert log returns to fractional.
        '''
        assert self.ts_type == TimeseriesType.RETURNS
        assert self.ts_sub_type == TimeseriesSubType.LOG
        new_returns = np.exp(self.__np_values).tolist()
        return Timeseries(self.dates, new_returns, self.ts_type, TimeseriesSubType.FRACTIONAL)

    def set_indicator_type(self, new_subtype):
        '''
        Set the time-series type information
        '''
        self.ts_type = TimeseriesType.INDICATOR
        self.ts_sub_type = new_subtype
