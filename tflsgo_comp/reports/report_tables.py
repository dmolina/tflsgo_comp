from .report_utils import normalize_df


def highlight_max(s):
    '''
    highlight the maximum in a Series yellow.
    '''
    is_min = s == s.min()
    return ['color: RoyalBlue' if v else '' for v in is_min]


def changecol(col):
    """Change Fx => F0x when x is a only digit

    :param col: column name
    :returns:  update column name
    :rtype: str

    """
    if not col.startswith('F'):
        return col
    elif len(col) > 2:
        return col
    else:
        return "F0{}".format(col[1])


def format_e(df):
    return {field: '{:5.2e}' for field in df.columns}


def create_tables(df, categories, accuracies, dimension=1000):
    """
    Create tables from the dataframe with the data, in format pandas.

    The datasets must have the structure:

    algorithm | f1 | f2 | ... | accuracy | dimension)

    :param df: dataframe with the values to compare.
    :param group: dict with for each category list the functions.
    :param categories: categories to compare (sorted).
    :param algs: Pandas.
    """
    table_g = normalize_df(df, dimension, accuracies)
    table_g.columns = [changecol(col) for col in table_g.columns]
    titles_idx = table_g['milestone'].unique().tolist()
    titles_idx.sort()
    tables = {}
    titles = {}

    for mil, table in table_g.groupby(['milestone']):
        table = table.transpose().drop('milestone')
        table.columns = table.loc['alg']
        table.drop('alg', inplace=True)
        table.sort_index(inplace=True)
        table.applymap(lambda x: float(x))
        # Remark in red
        # Change the index name
        table.columns.names = ['Functions']
        style = table.style.apply(highlight_max, axis=1).format(format_e(table))
        tables[mil] = style.render()
        titles[mil] = "Accuracy: {:2.1e}".format(mil)

    return titles_idx, titles, tables

def create_figures(df, categories, accuracies, libplot, dimension=1000, mobile=False):
    return libplot.to_json([])
