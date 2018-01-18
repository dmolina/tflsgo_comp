"""
This file contains the wrapper for the plot API using the Holoviews and
Bokeh libraries.
"""
import holoviews as hv
from bokeh.embed import components
import itertools

renderer = ""

def init():
    """Init the resource
    """
    global renderer
    hv.extension('bokeh')
    renderer = hv.renderer('bokeh')


def formatter(num):
    """
    Print results using exponential.
    Warning: The source code is not python, but JavaScript, to be used for
    Bokeh formatter.

    :param num: number to format.
    """
    return num.toExponential(2)


def _plot_line(df, x, y, label, xaxis, yaxis, logy, xticks=None, show_legend=True):
    global hv

    options_plot = dict({'logy': logy, 'xticks': xticks, 'show_legend': show_legend,
                         'sizing_mode': 'scale_both'})

    if xticks:
        options_plot.update({'xticks': xticks})

    hv.opts({'Curve': {'plot': options_plot}, 'NdOverlay': {'plot':
                                                            {'legend_position':
                                                             'right'}}})
    dim_x = hv.Dimension(x, label=label, value_format=formatter)
    curve = hv.Curve(df, dim_x, y)
    return curve


def get_plot_function(type):
    if type == 'line':
        return _plot_line


def setSize(size):
    global renderer

    if size:
        renderer = renderer.instance(size=size)


def plot(df, x, y, label=None, xticks=None, xaxis=None, yaxis=None, logy=False,
         show_legend=True, groupby=None, group_label='',
         groupby_transform=None, hue=None, cols=1, kind='line', size=None,
         scientific_format=True):
    kinds = ['line']
    setSize(size)

    if kind not in kinds:
        kinds_str = ",".join(kinds)
        error = "kind is not known, it must be in [{}]".format(kinds_str)
        raise ValueError(error)

    if groupby is None and label is None:
        error = "label is mandatory without groupby"
        raise ValueError(error)

    plot_elem = get_plot_function(kind)

    if xaxis is None:
        xaxis = x.title()

    if yaxis is None:
        yaxis = y.title()

    options_plot = dict(x=x, xaxis=xaxis, yaxis=yaxis, show_legend=show_legend,
                        logy=logy)

    if xticks:
        options_plot.update({'xticks': xticks})

    if groupby is None:
        return plot_elem(df, y=y, label=label, **options_plot)
    else:
        if type(groupby) is not list:
            groupby = ["{}".format(groupby)]

        values = df[hue].unique().tolist()
        comb = itertools.product(values, groupby)

        if not groupby_transform:
            t = lambda x: x
        else:
            t = groupby_transform

        plots = {(val_hue, t(group)): plot_elem(df[df[hue]==val_hue], y=group, label=val_hue,
                                          **options_plot) for val_hue, group in comb}

        kdims = [hv.Dimension(elem, label=elem.title()) for elem in [hue, group_label]]
        holomap = hv.HoloMap(plots, kdims=kdims)
        plot = holomap.overlay(hue).layout(group_label.title()).cols(cols)
        return renderer.get_plot(plot).state


def to_json(plots):
    """Make the figure visualize with the json.

    :param fig_names: name of the figs
    :param plots: plots to visualize
    :param libcharts: type of plot library (hv is currently only supported)
    :returns: dictionary of type
    :rtype: {'error': ...,'plots': [{'title': .., 'js': ..,  'tags': ..}, ..]}
    """
    result = dict()

    script, divs = components(plots, wrap_script=False)
    result['js'] = script
    result['divs'] = divs
    result.update({'error': '', 'type': 'hv'})
    return result

