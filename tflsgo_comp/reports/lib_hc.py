"""
This file contains the wrapper for the plot API using the HighCharts
libraries. https://www.highcharts.com/products/highcharts/
It is free for non-commercial usage
"""
import pandas as pd
from pandas_highcharts.core import serialize


def plot(df, x, y, label=None, xticks=None, xaxis=None, yaxis=None, logy=False,
         show_legend=True, groupby=None, group_label='',
         groupby_transform=None, hue=None, cols=1, kind='line', size=None):
    params = dict(figsize=size, zoom="xy", logy=logy)

    if xticks:
        params.update(dict(xticks=xticks))

    if groupby is None and label is None:
        error = "label is mandatory without groupby"
        raise ValueError(error)

    if xaxis is None:
        xaxis = x.title()

    if yaxis is None:
        yaxis = y.title()

    params = dict(show_legend=show_legend, logy=logy)

    def changeXY(value):
        if value == x:
            return xaxis
        elif value == y:
            return yaxis
        else:
            return value

    if xticks:
        params.update({'xticks': xticks})

    if groupby is None:
        return [serialize.plot_elem(df, y=y, **params)]
    else:
        if type(groupby) is not list:
            groupby = ["{}".format(groupby)]

        plot_df = df.pivot(index=x, columns=hue)
        plots = []

        for i, group in enumerate(groupby):
            group_df = plot_df[group]
            group_df.index.names = [xaxis]
            plot = serialize(group_df, output_type='json', **params, render_to='figures{}'.format(i+1))
            print(plot)
            plots.append(plot)

        return plots


def to_json(plots):
    """Make the figure visualize with the json.

    :param fig_names: name of the figs
    :param plots: plots to visualize
    :param libcharts: type of plot library (hv is currently only supported)
    :returns: dictionary of type
    :rtype: {'error': ...,'plots': [{'title': .., 'js': ..,  'tags': ..}, ..]}
    """
    # import ipdb; ipdb.set_trace()
    result = dict()
    error = ''
    result.update({'figures': list(plots.values())[0]})
    result.update({'error': error, 'type': 'highcharts'})
    return result
