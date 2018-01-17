"""
This file contains the functions used to show figures of convergence for the
benchmark, using the milestones as references.
"""
from .report_utils import figure_json, load_charts_library


def create_tables(df, categories, accuracies, dimension=1000):
    return [], {}, {}


def create_figures(df, categories, accuracies, dimension=1000, mobile=False, libcharts='hv'):
    """
    Create convergence figures.

    The datasets must have the structure:

    algorithm | f1 | f2 | ... | accuracy | dimension)

    :param df: dataframe with the values to compare.
    :param group: dict with for each category list the functions.
    :param categories: categories to compare (sorted).
    :param algs: algorithm list (sorted).
    """
    libplot = load_charts_library(libcharts)
    mean = {col: 'mean' for col in df.columns if col.startswith('F')}
    df = df.groupby(['alg', 'milestone']).agg(mean).reset_index()

    xticks = [0] + accuracies
    # Get the functions to visualize
    funs_str = [col for col in df.columns if col.startswith('F')]

    def fun_to_int(fun):
        return int(fun[1:])

    plot = libplot.plot(df, x='milestone', xaxis='Evaluations', xticks=xticks,
                        y='mean', yaxis='Error', logy=True, show_legend=True,
                        hue='alg', groupby=funs_str,
                        groupby_transform=fun_to_int, group_label='Function',
                        kind='line', size=200, scientific_format=True)

    figures = {'Convergence Functions': plot}
    return libplot.to_json(figures)
