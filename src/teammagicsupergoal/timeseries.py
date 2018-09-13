import pandas as pd
import numpy as np
import logging as log

class TimeseriesType:
    PRICE = "Price"
    RETURNS = "Returns"
    VOL = "Volatility"

class TimeseriesSubType:
    FRACTIONAL = "Fractional"
    LOG = "Logarithmic"
    ABSOLUTE = "Absolute"
    RELATIVE = "Relative"
    EMA = "Exp. weighted Moving Av."
    AVERAGE = "Equally weighted Av."

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

        new_ts = Timeseries(new_dates, np_new_values.toList(), TimeseriesType.RETURNS, returns_type, period)
        return new_ts
        
        