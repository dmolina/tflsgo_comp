"""
This file contains the functions used to create tables and figures for the
CEC'2013 benchmark.

"""
import numpy as np
import pandas as pd

from .report_utils import figure_json

import holoviews as hv

from .report_utils import normalize_df

from .report_utils import get_plot_bar
from .report_utils import figure_json


def _get_values_df(df, functions):
    # Obtain the rank
    data_df = df.drop('milestone', 1).set_index('alg')
    rank_df = data_df.rank()
    # Change the rank position by the f1 value
    values_df = rank_df[functions].apply(get_f1_score)
    # Sum all functions
    sum_df = values_df.sum(axis=1).reset_index()
    # Put name to aggregate column
    sum_df.columns = ['alg', 'Value']
    return sum_df


def create_tables(df, categories, accuracies, dimension=1000):
    return [], {}, {}


def _get_all_f1(df, categories, milestones):
    num_rows, num_columns = df.shape
    num_functions = num_columns-3
    assert(num_functions > 0)
    # append all data in a pivot table
    total_pivot_df = pd.DataFrame(index=np.arange(0, num_rows*len(categories)),
                                  columns=('category', 'milestone', 'alg',
                                           'ranking'))

    pivot_i = 0

    for cat in categories:
        # Filter only the function in the category
        functions = ['F{}'.format(x) for x in cat.functions()]
        milestones.sort()

        # Create  total_pivot_df
        for milestone in milestones:
            current_df = df[df['milestone'] == milestone]

            if not current_df.empty:
                # Remove field milestone and index by alg
                # current_df = current_df.drop('milestone', 1).set_index('alg')
                # Add to total value
                sum_df = _get_values_df(current_df, functions)
                # Add extra information

                for alg, rank in sum_df.values:
                    new_ranking_row = [cat.name, milestone, alg, rank]
                    total_pivot_df.loc[pivot_i] = new_ranking_row
                    pivot_i += 1

    return total_pivot_df


def create_figures(df, categories, accuracies, libplot, dimension=1000, mobile=False):
    """
    Create graphics from the dataframe with the data.

    The datasets must have the structure:

    algorithm | f1 | f2 | ... | accuracy | dimension)

    :param df: dataframe with the values to compare.
    :param group: dict with for each category list the functions.
    :param categories: categories to compare (sorted).
    :param algs: algorithm list (sorted).
    """
    milestones = df['milestone'].unique().tolist()
    milestones = accuracies
    milestones.sort()
    dim_df = normalize_df(df, dimension, accuracies)
    values_df = _get_all_f1(dim_df, categories, milestones)

    titles = dict(alg='Algorithm', ranking='Points', milestone='Evaluations',
                  category='Categories')

    if mobile:
        num_cols = 1
    else:
        num_cols = 3

    total_figs = {}
    fig_names = []

    # Plotting
    cat_names = [cat.name for cat in categories]

    def formatter(value):
        return "Accuracy: {:.3e}".format(value)

    for cat in cat_names:
        cat_df = values_df[values_df['category'] == cat]
        plot = libplot.plot_bar(cat_df, titles=titles, x='alg', y='ranking',
                                groupby='milestone',
                                groupby_transform=formatter, rotation=True,
                                size=None, num_cols=num_cols)
        total_figs[cat] = plot

    plot_stacked = libplot.plot_bar_stack(values_df, titles=titles, x='alg',
                                          y='ranking', groupby='milestone',
                                          groupby_values=milestones,
                                          groupby_transform=formatter,
                                          rotation=True, hue='category',
                                          hue_values=cat_names, size=100,
                                          num_cols=num_cols)

    total_figs['All'] = plot_stacked

    return libplot.to_json(total_figs)
 
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
