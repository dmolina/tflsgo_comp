"""
This file contains the functions used to create tables and figures for the
CEC'2013 benchmark.

"""
import numpy as np
import pandas as pd

from dfply import *

import holoviews as hv

from .report_utils import get_plot_bar
from .report_utils import figure_json


def _get_values_df(data_df, functions):
    # Obtain the rank
    rank_df = data_df.rank()
    # Change the rank position by the f1 value
    values_df = rank_df[functions].apply(get_f1_score)
    # Sum all functions
    sum_df = values_df.sum(axis=1).reset_index()
    # Put name to aggregate column
    sum_df.columns = ['alg', 'Value']
    return sum_df


def plot_global(df):
    df['ranking'] = df['ranking'].astype(int)
    milestones = df['milestone'].unique()
    plots = []

    for milestone in milestones:
        m_df = df[df['milestone'] == milestone]
        category = df['category'].unique()
        total = pd.pivot_table(m_df, values='ranking', index=['alg'],
                               columns=['category']).reset_index()
        plot = get_plot_barh(total, category, "Probando de nuevo con leyenda")
        plots.append(plot)

    return hv.Layout(plots).cols(3)


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


def highlight_max(s):
    '''
    highlight the maximum in a Series yellow.
    '''
    is_min = s == s.min()
    return ['color: RoyalBlue' if v else '' for v in is_min]


def format_e(df):
    return {field: '{:5.2e}' for field in df.columns}


def get_plot_by_milestone(df, mil):
    table = df[df['milestone'] == mil]
    return get_plot_barh(table, "Accuracy: {:2.1E}".format(mil))

def cec2013_normalize(df, dimension):
    milestones = [int(1.2e5), int(6e5), int(3e6)]
    dim_df = df >> mask(X.dimension == dimension) >> drop(X.id, X.dimension)
    # Filter the milestone
    dim_df = dim_df[dim_df['milestone'].isin(milestones)]
    table_g = dim_df

    table_g['milestone'] = table_g['milestone'].astype(int)
    mean = {col: 'mean' for col in table_g.columns if col.startswith('F')}
    table_g = table_g.groupby(['alg', 'milestone']).agg(mean).reset_index()
    return table_g


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
    table_g = cec2013_normalize(df, dimension)
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


def get_plot_barh(df, title):
    """Return a bar plot with the data and the title

    :param data_df: dataframe with the data.
    :param title: title for the plot.
    :returns: A plot (bokeh plot).
    :rtype: bokeh plot.
    """
    # Prepare to visualize
    kdims = [('alg', 'Algorithm'), ('category', 'Category'), ('ranking', 'Ranking')]
    # Plot the bar
    fields = ['alg', 'category', 'ranking']
    data_df = df[fields].sort_values(['alg'])
    data = [tuple(row) for row in data_df.values]
    options = "Bars [tools=['hover'] stack_index=1 color_index=1 show_legend=False xrotation=90]"
    bar = hv.Bars(data, kdims[:2], kdims[2], label=title)
    return bar.opts(options)


def create_figures(df, categories, accuracies, dimension=1000, mobile=False):
    """
    Create graphics from the dataframe with the data.

    The datasets must have the structure:

    algorithm | f1 | f2 | ... | accuracy | dimension)

    :param df: dataframe with the values to compare.
    :param group: dict with for each category list the functions.
    :param categories: categories to compare (sorted).
    :param algs: algorithm list (sorted).
    """
    num_cols = 3
    dim_df = cec2013_normalize(df, dimension)
    milestones = dim_df['milestone'].unique().tolist()
    milestones.sort()

    if mobile:
        num_cols = 1

    hv.extension('bokeh')
    renderer = hv.renderer('bokeh')
    options = "Bars [xrotation=90]"

    total_figs = {}
    fig_names = []

    num_rows, num_columns = dim_df.shape
    num_functions = num_columns-3
    assert(num_functions > 0)
    # append all data in a pivot table
    total_pivot_df = pd.DataFrame(index=np.arange(0, num_rows*len(categories)),
                                  columns=('category', 'milestone', 'alg',
                                           'ranking'))
    pivot_i = 0

    for cat in categories:
        cat_name = cat.name
        # Filter only the function in the category
        functions = ['F{}'.format(x) for x in cat.functions()]
        cat_figs = []
        accuracies.sort()

        for milestone in milestones:
            current_df = dim_df >> mask(X.milestone == milestone)

            if not current_df.empty:
                # Remove field milestone and index by alg
                current_df = current_df.drop('milestone', 1).set_index('alg')
                # Add to total value
                sum_df = _get_values_df(current_df, functions)
                title = "Accuracy: {:2.1E}".format(milestone)
                plot = get_plot_bar(sum_df, title)
                cat_figs.append(plot)
                # Add extra information

                for alg, rank in sum_df.values:
                    new_ranking_row = [cat_name, milestone, alg, rank]
                    total_pivot_df.loc[pivot_i] = new_ranking_row
                    pivot_i += 1

            total_figs[cat_name] = renderer.get_plot(hv.Layout(cat_figs).opts(options).cols(num_cols)).state

    cat_global = []

    plot_dyn = {}

    for mil in milestones:
        plot = get_plot_by_milestone(total_pivot_df, mil)
        plot_dyn[mil] = plot
        cat_global.append(plot)

    plots = hv.Layout(cat_global).opts(options)
    # legend_opts = {'NdOverlay': dict(show_legend=True, legend_position='right')}
    # plots.Bars.III = plots.Bars.III(plot=legend_opts)
    total_figs['All'] = renderer.get_plot(plots.cols(num_cols)).state
    fig_names.extend([cat.name for cat in categories])
    fig_names.append('All')

    return figure_json(fig_names, total_figs)

    final = hv.NdLayout(plot_dyn, kdims='milestone')
    total_figs['Final'] = renderer.get_plot(final).state
    fig_names.append('Final')
    plot_bokeh = renderer.get_plot(hv.HoloMap(plot_dyn)).state
    setattr(plot_bokeh, 'plot_width', 500)
    setattr(plot_bokeh, 'plot_height', 300)
    total_figs['Final2'] = plot_bokeh
    fig_names.append('Final2')

    return figure_json(fig_names, total_figs)

 
def get_f1_score(position):
    """
    Return a np.array with the scoring criterio by position from the Formula 1,
    in which the first 10 items have scores. The array have position.

    - If position is lower than 10, it is shorten.
    - If position is greater than 10, it is increased with 0s.

    :param position: position of the algorithm.
    """
    f1 = np.array([0, 25, 18, 15, 12, 10, 8, 6, 4, 2, 1])
    pos = np.floor(position).astype(int)
    pos[pos > 10] = 0
    return f1[pos]
