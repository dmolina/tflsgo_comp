from bokeh.plotting import figure
import pandas as pd
import numpy as np

from .report_utils import figure_json
import holoviews as hv


def create_tables(df, categories, accuracies, dimension=1000):
    return {}, {}, {}

def create_figures(df, categories, accuracies, dimension=1000):
    hv.extension('bokeh')
    renderer = hv.renderer('bokeh')

    xs = range(-10, 11)
    ys = [100+x**2 for x in xs]
    ys2 = [10+x**3 for x in xs]
    plot_hv = hv.Curve((xs, ys))
    plot1 = renderer.get_plot(plot_hv).state
    plot_hv = hv.Curve((xs, ys2))
    plot2 = renderer.get_plot(plot_hv).state
    plots = {'Titulo1': plot1, 'Titulo2': plot2}
    return figure_json(plots.keys(), plots)
