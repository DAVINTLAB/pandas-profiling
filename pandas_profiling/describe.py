# -*- coding: utf-8 -*-
"""Compute statistical description of datasets"""
import multiprocessing
import itertools
from functools import partial
import numpy as np
import pandas as pd
import matplotlib

from pkg_resources import resource_filename
import pandas_profiling.formatters as formatters
import pandas_profiling.base as base
import pandas_profiling.correlation as correlation
from pandas_profiling.plot import histogram, mini_histogram

def describe_numeric_1d(series, **kwargs):
    """Compute summary statistics of a numerical (`TYPE_NUM`) variable (a Series).

    Also create histograms (mini an full) of its distribution.

    Parameters
    ----------
    series : Series
        The variable to describe.

    Returns
    -------
    Series
        The description of the variable as a Series with index being stats keys.
    """
    # Format a number as a percentage. For example 0.25 will be turned to 25%.
    _percentile_format = "{:.0%}"

    stats = {}

    stats['type'] = base.TYPE_NUM
    stats['mean'] = series.mean()
    stats['std'] = series.std()
    stats['variance'] = series.var()
    stats['min'] = series.min()
    stats['max'] = series.max()
    stats['range'] = stats['max'] - stats['min']
    # To avoid to compute it several times
    _series_no_na = series.dropna()
    for percentile in np.array([0.05, 0.25, 0.5, 0.75, 0.95]):
        # The dropna() is a workaround for https://github.com/pydata/pandas/issues/13098
        stats[_percentile_format.format(percentile)] = _series_no_na.quantile(percentile)
    stats['iqr'] = stats['75%'] - stats['25%']
    stats['kurtosis'] = series.kurt()
    stats['skewness'] = series.skew()
    stats['sum'] = series.sum()
    stats['mad'] = series.mad()
    stats['cv'] = stats['std'] / stats['mean'] if stats['mean'] else np.NaN
    stats['n_zeros'] = (len(series) - np.count_nonzero(series))
    stats['p_zeros'] = stats['n_zeros'] / len(series)
    # Histograms
    stats['histogram'] = histogram(series, **kwargs)
    stats['mini_histogram'] = mini_histogram(series, **kwargs)

    return pd.Series(stats, name=series.name)

def describe_date_1d(series, **kwargs):
    """Compute summary statistics of a date (`TYPE_DATE`) variable (a Series).

    Also create histograms (mini an full) of its distribution.

    Parameters
    ----------
    series : Series
        The variable to describe.

    Returns
    -------
    Series
        The description of the variable as a Series with index being stats keys.
    """
    stats = {}

    stats['min'] = series.min()
    stats['max'] = series.max()
    stats['range'] = stats['max'] - stats['min']
    stats['histogram'] = histogram(series, **kwargs)
    stats['mini_histogram'] = mini_histogram(series, **kwargs)
    stats['type'] = base.TYPE_DATE

    return pd.Series(stats, name=series.name)

def describe_categorical_1d(series, **kwargs):
    """Compute summary statistics of a categorical (`TYPE_CAT`) variable (a Series).

    Parameters
    ----------
    series : Series
        The variable to describe.

    Returns
    -------
    Series
        The description of the variable as a Series with index being stats keys.
    """
    # Only run if at least 1 non-missing value
    value_counts, distinct_count = base.get_groupby_statistic(series)

    stats = {}

    if base.get_vartype(series) == base.TYPE_CAT:
        contains = {
            'chars': series.str.contains(r'[a-zA-Z]', case=False, regex=True).any(),
            'digits': series.str.contains(r'[0-9]', case=False, regex=True).any(),
            'spaces': series.str.contains(r'\s', case=False, regex=True).any(),
            'non-words': series.str.contains(r'\W', case=False, regex=True).any(),
        }

        stats['top'] = value_counts.index[0]
        stats['freq'] = value_counts.iloc[0]
        stats['max_length'] =  series.str.len().max()
        stats['mean_length'] = series.str.len().mean()
        stats['min_length'] =  series.str.len().min()
        stats['composition'] = contains
        stats['type'] = base.TYPE_CAT

    return pd.Series(stats, name=series.name)

def describe_boolean_1d(series, **kwargs):
    """Compute summary statistics of a boolean (`TYPE_BOOL`) variable (a Series).

    Parameters
    ----------
    series : Series
        The variable to describe.

    Returns
    -------
    Series
        The description of the variable as a Series with index being stats keys.
    """
    value_counts, distinct_count = base.get_groupby_statistic(series)

    stats = {}

    stats['top'] = value_counts.index[0]
    stats['freq'] = value_counts.iloc[0]
    stats['mean'] = series.mean()
    stats['type'] = base.TYPE_BOOL

    return pd.Series(stats, name=series.name)

def describe_constant_1d(series, **kwargs):
    """Compute summary statistics of a constant (`S_TYPE_CONST`) variable (a Series).

    Parameters
    ----------
    series : Series
        The variable to describe.

    Returns
    -------
    Series
        The description of the variable as a Series with index being stats keys.
    """
    return pd.Series([base.S_TYPE_CONST], index=['type'], name=series.name)

def describe_unique_1d(series, **kwargs):
    """Compute summary statistics of a unique (`S_TYPE_UNIQUE`) variable (a Series).

    Parameters
    ----------
    series : Series
        The variable to describe.

    Returns
    -------
    Series
        The description of the variable as a Series with index being stats keys.
    """
    return pd.Series([base.S_TYPE_UNIQUE], index=['type'], name=series.name)

def describe_supported(series, **kwargs):
    """Compute summary statistics of a supported variable (a Series).

    Parameters
    ----------
    series : Series
        The variable to describe.

    Returns
    -------
    Series
        The description of the variable as a Series with index being stats keys.
    """
    length = len(series)  # number of observations in the Series

    value_counts, distinct_count = base.get_groupby_statistic(series)

    stats = {}

    stats['count'] = series.count()  # number of non-NaN observations in the Series
    stats['distinct_count'] = distinct_count
    stats['p_missing'] = 1 - stats['count'] / length
    stats['n_missing'] = length - stats['count']
    stats['n_infinite'] = stats['count'] - series.count()  # number of infinte observations in the Series
    stats['p_infinite'] = stats['n_infinite'] / length
    stats['is_unique'] = distinct_count == length
    stats['mode'] = series.mode().iloc[0] if stats['count'] > distinct_count > 1 else series[0]
    stats['p_unique'] = distinct_count / length

    try:
        # pandas 0.17 onwards
        stats['memorysize'] = series.memory_usage()
    except:
        stats['memorysize'] = 0

    return pd.Series(stats, name=series.name)

def describe_unsupported(series, **kwargs):
    """Compute summary statistics of a unsupported (`S_TYPE_UNSUPPORTED`) variable (a Series).

    Parameters
    ----------
    series : Series
        The variable to describe.

    Returns
    -------
    Series
        The description of the variable as a Series with index being stats keys.
    """
    length = len(series)  # number of observations in the Series

    stats = {}

    stats['count'] = series.count()
    stats['p_missing'] = 1 - stats['count'] / length
    stats['n_missing'] = length - stats['count']
    stats['n_infinite'] = stats['count'] - series.count()  # number of infinte observations in the Series
    stats['p_infinite'] = stats['n_infinite'] / length
    stats['type'] = base.S_TYPE_UNSUPPORTED

    try:
        # pandas 0.17 onwards
        stats['memorysize'] = series.memory_usage()
    except:
        stats['memorysize'] = 0

    return pd.Series(stats, name=series.name)

def describe_1d(data, **kwargs):
    """Compute summary statistics of a variable (a Series).

    The description is different according to the type of the variable.
    However a set of common stats is also computed.

    Parameters
    ----------
    series : Series
        The variable to describe.

    Returns
    -------
    Series
        The description of the variable as a Series with index being stats keys.
    """

    # Replace infinite values with NaNs to avoid issues with
    # histograms later.
    data.replace(to_replace=[np.inf, np.NINF, np.PINF], value=np.nan, inplace=True)

    result = pd.Series({}, name=data.name)

    vartype = base.get_vartype(data)

    if vartype == base.S_TYPE_UNSUPPORTED:
        result = result.append(describe_unsupported(data))
    else:
        result = result.append(describe_supported(data))

        if vartype == base.S_TYPE_CONST:
            result = result.append(describe_constant_1d(data, **kwargs))
        elif vartype == base.TYPE_BOOL:
            result = result.append(describe_boolean_1d(data, **kwargs))
        elif vartype == base.TYPE_NUM:
            result = result.append(describe_numeric_1d(data, **kwargs))
        elif vartype == base.TYPE_DATE:
            result = result.append(describe_date_1d(data, **kwargs))
        elif vartype == base.S_TYPE_UNIQUE:
            result = result.append(describe_unique_1d(data, **kwargs))
        else:
            # TYPE_CAT
            result = result.append(describe_categorical_1d(data, **kwargs))

    return result

def multiprocess_func(x, **kwargs):
    return x[0], describe_1d(x[1], **kwargs)

def describe(df, check_correlation=True, correlation_threshold=0.9, correlation_overrides=None, check_recoded=False, pool_size=multiprocessing.cpu_count(), **kwargs):
    """Generates a dict containing summary statistics for a given dataset stored as a pandas `DataFrame`.

    Used has is it will output its content as an HTML report in a Jupyter notebook.

    Parameters
    ----------
    df : DataFrame
        Data to be analyzed
    bins : int
        Number of bins in histogram.
        The default is 10.
    check_correlation : boolean
        Whether or not to check correlation.
        It's `True` by default.
    correlation_threshold: float
        Threshold to determine if the variable pair is correlated.
        The default is 0.9.
    correlation_overrides : list
        Variable names not to be rejected because they are correlated.
        There is no variable in the list (`None`) by default.
    check_recoded : boolean
        Whether or not to check recoded correlation (memory heavy feature).
        Since it's an expensive computation it can be activated for small datasets.
        `check_correlation` must be true to disable this check.
        It's `False` by default.
    pool_size : int
        Number of workers in thread pool
        The default is equal to the number of CPU.

    Returns
    -------
    dict
        Containing the following keys:
            * table: general statistics on the dataset
            * variables: summary statistics for each variable
            * freq: frequency table

    Notes:
    ------
        * The section dedicated to check the correlation should be externalized
    """

    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be of type pandas.DataFrame")
    if df.empty:
        raise ValueError("df can not be empty")

    try:
        # reset matplotlib style before use
        # Fails in matplotlib 1.4.x so plot might look bad
        matplotlib.style.use("default")
    except:
        pass

    matplotlib.style.use(resource_filename(__name__, "pandas_profiling.mplstyle"))
    
    # Clearing the cache before computing stats
    base.clear_cache()

    if not pd.Index(np.arange(0, len(df))).equals(df.index):
        # Treat index as any other column
        df = df.reset_index()

    # Describe all variables in a univariate way
    pool = multiprocessing.Pool(pool_size)
    local_multiprocess_func = partial(multiprocess_func, **kwargs)
    ldesc = {col: s for col, s in pool.map(local_multiprocess_func, df.iteritems())}
    pool.close()

    if check_correlation:
        corrMatrixPear = correlation.pearson_corr(df)
        corrMatrixSpear = correlation.spearman_cor(df)
        corrMatrixCramers = correlation.cramers_corr(df)
        corrMatrixRecoded = correlation.recoded_corr(df) if check_recoded else None

        corrThresPear = correlation.overthreshold_corr(corrMatrixPear, "CORR", lambda corr: corr > correlation_threshold)
        corrThresCramers = correlation.overthreshold_corr(corrMatrixCramers, "CORR", lambda corr: corr > correlation_threshold)
        corrThresRecoded = correlation.overthreshold_corr(corrMatrixRecoded, "RECODED", lambda corr: corr) if check_recoded else {}

        ldesc.update(corrThresPear)
        ldesc.update(corrThresCramers)
        ldesc.update(corrThresRecoded)

        correlation_stats = {
            'pearson': corrMatrixPear,
            'spearman': corrMatrixSpear,
            'cramers': corrMatrixCramers,
            'recoded': corrMatrixRecoded
        }
    else:
        correlation_stats = None

    # Convert ldesc to a DataFrame
    names = []
    ldesc_indexes = sorted([x.index for x in ldesc.values()], key=len)
    for idxnames in ldesc_indexes:
        for name in idxnames:
            if name not in names:
                names.append(name)
    variable_stats = pd.concat(ldesc, join_axes=pd.Index([names]), axis=1)
    variable_stats.columns.names = df.columns.names

    # General statistics
    table_stats = {}

    table_stats['n'] = len(df)
    table_stats['nvar'] = len(df.columns)
    table_stats['n_cells_missing'] = variable_stats.loc['n_missing'].sum()
    table_stats['p_cells_missing'] = table_stats['n_cells_missing'] / (table_stats['n'] * table_stats['nvar'])

    supported_columns = variable_stats.transpose()[variable_stats.transpose().type != base.S_TYPE_UNSUPPORTED].index.tolist()
    table_stats['n_duplicates'] = sum(df.duplicated(subset=supported_columns)) if len(supported_columns) > 0 else 0
    table_stats['p_duplicates'] = (table_stats['n_duplicates'] / len(df)) if (len(supported_columns) > 0 and len(df) > 0) else 0

    memsize = df.memory_usage(index=True).sum()
    table_stats['memsize'] = formatters.fmt_bytesize(memsize)
    table_stats['recordsize'] = formatters.fmt_bytesize(memsize / table_stats['n'])

    table_stats.update({k: 0 for k in ("NUM", "DATE", "CONST", "CAT", "UNIQUE", "CORR", "RECODED", "BOOL", "UNSUPPORTED")})
    table_stats.update(dict(variable_stats.loc['type'].value_counts()))
    table_stats['REJECTED'] = table_stats['CONST'] + table_stats['CORR'] + table_stats['RECODED']

    return {
        'table': table_stats,
        'variables': variable_stats.T,
        'freq': {k: (base.get_groupby_statistic(df[k])[0] if variable_stats[k].type != base.S_TYPE_UNSUPPORTED else None) for k in df.columns},
        'correlations': correlation_stats
    }