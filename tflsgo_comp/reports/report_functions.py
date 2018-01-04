"""
This file contains the functions used to show figures of convergence for the
benchmark, using the milestones as references.
"""
import holoviews as hv
from .report_utils import figure_json

from bokeh.models.formatters import PrintfTickFormatter


def create_tables(df, categories, accuracies, dimension=1000):
    return [], {}, {}


def create_figures(df, categories, accuracies, dimension=1000):
    """
    Create convergence figures.

    The datasets must have the structure:

    algorithm | f1 | f2 | ... | accuracy | dimension)

    :param df: dataframe with the values to compare.
    :param group: dict with for each category list the functions.
    :param categories: categories to compare (sorted).
    :param algs: algorithm list (sorted).
    """
    hv.extension('bokeh')
    renderer = hv.renderer('bokeh')

    def formatter(num):
        return num.toExponential(2)

    fig_names = []
    figures = {}
    titles = {}

    options_plot = dict({'logy': True, 'xticks': 4, 'show_legend': True, 'width': 600, 'height': 300})
    options_plot['xticks'] = [0] +accuracies
    print(options_plot['xticks'])
    hv.opts({'Curve': {'plot': options_plot},
             'NdOverlay': {'plot': {'legend_position': 'right'}}})

    def figure_conv(df, alg, function):
        fun = "F{}".format(function)
        milestone = hv.Dimension('milestone', label='Evaluation', value_format=formatter)
        curve = hv.Curve(df[df['alg'] == alg], milestone, fun)
        return curve

    # Get the functions
    funs = [col for col in df.columns if col.startswith('F')]
    funs = [int(fun[1:]) for fun in funs]
    curves = {(alg, fun): figure_conv(df, alg, function=fun) for alg in
              df['alg'].unique().tolist() for fun in funs}
    kdims = [hv.Dimension('alg', label='Algorithm'),
             hv.Dimension('function', label='Function')]
    holomap = hv.HoloMap(curves, kdims=kdims)
    # holomap  = holomap.options({'show_legend': True})
    hv.output("size=130")
    plot = holomap.overlay('Algorithm').layout('Function').cols(1)
    # plot[2] = plot[2].opts("Curve [show_legend=True]")
    fig_names = ['test']
    figures['test'] = renderer.get_plot(plot).state
    titles['test'] = 'Convergence Functions'
    return figure_json(fig_names, figures)
