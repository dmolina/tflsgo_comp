
from os.path import splitext

import pandas as pd


def read_results_from_file(algname, fullname):
    """
    Read the results of an algorithm using pandas library.

    :param algname: algname (only if alg is defined)
    :param fullname: full name from algorithm

    """
    name, ext = splitext(fullname)
    error = ''

    if ext in ['.xls', '.xlsx']:
        data = pd.read_excel(fullname, converters={'milestone': str})
    elif ext in ['.csv']:
        data = pd.read_csv(fullname)
    else:
        error = 'Format of file \'{}\' not valide (.xls or .csv)'.format(fullname)

    data_norm = normalize_data(data, algname)
    return data_norm, error


def normalize_data(df, algname):
    """
    Generate normalize_data.

    :param df: data frame
    :param algname: algorithm name
    :returns: normalizeddata frame
    :rtype: pandas.DataFrame
    """
    def lower_upper(column):
        if column.startswith("F") or column.startswith("f"):
            return column.upper()
        else:
            return column.lower()

    # Minimize the column alg and milestone
    df.columns = [lower_upper(col) for col in df.columns]
    functions = [f for f in df.columns if f.startswith('F')]

    if 'alg' not in df.columns:
        df['alg'] = algname

    # Sorted columns
    cols = ['alg', 'milestone']+functions
    return df[cols]


def error_in_data(df, nfuns, milestones_benchmark):
    """
    Check the data frame.

    :param df: data frame
    :param bench: related benchmark (to compare)
    :param milestones_benchmark: milestones that df must follow
    """
    milestone_str = 'milestone'

    # Check milestone column
    if milestone_str not in df.columns:
        return "missing column '{}'".format(milestone_str)

    # Check that all column are right
    funs = ['F{}'.format(nfun) for nfun in range(1, nfuns+1)]

    for fun in funs:
        if fun not in df.columns:
            return "function '{}' not found in {}".format(fun, df.columns)

    # Check not additional column
    pending_columns = set(df.columns)-set(funs)-{'milestone', 'alg', 'dimension'}

    if pending_columns:
        return "columns '{}' are unknown".format(pending_columns)

    min_value = float(df[funs].min(axis=1).min())

    # Check all positive values
    if min_value < 0:
        return "negative value '{}' found".format(min_value)

    # Check all milestone
    milestones_data = df['milestone'].astype(float).astype(int).tolist()
    milestones_benchmark = [int(float(mil_bench)) for mil_bench in milestones_benchmark]
    print(milestones_benchmark)
    print(milestones_data)

    # For each milestone check that exists
    for milestone in milestones_benchmark:
        if milestone not in milestones_data:
            return "milestone '{}' not found".format(milestone)

    pending_milestones = set(milestones_benchmark)-set(milestones_data)

    if pending_milestones:
        return "milestone '{}' uknown".format(pending_milestones[0])

    return ""

def get_mean(df):
    """
    Get the mean of a data frame, grouping by algorithm and milestone.

    :param df: data frame
    :returns: data frame
    :rtype: pandas.DataFrame
    """
    data_mean = df.groupby('alg,milestone').mean()
    return data_mean.reset_index()

def concat_df(df1, df2):
    """Concat two dataframes.

    :param df1: dataframe1.
    :param df2: dataframe2.
    :returns: the dataframe joining by rows
    :rtype: pandas.DataFrame
    """
    if not df1:
        return df2

    if not df2:
        return df1

    return pd.concat([df1, df2]).reset_index().drop('index', axis=1)


def empty_data():
    """Return an empty dataframe

    :returns: A empty database
    :rtype: pandas.DataFrame

    """
    return pd.DataFrame({})
