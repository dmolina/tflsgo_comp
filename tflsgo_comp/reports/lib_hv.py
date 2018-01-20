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

        plots = {(val_hue, t(group)): plot_elem(df[df[hue] == val_hue], y=group, label=val_hue,
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


def plot_bar(df, titles, x, y, groupby=None, groupby_values=None, groupby_transform=None,
             rotation=False, size=None, title=None, num_cols=3):
    """Plot the dataframes as bar plots.

    :param df: dataframe.
    :param titles: dictionary that related the dimension with its name.
    :param x: axis to show.
    :param y: variable to show.
    :param groupby: groupby parameter.
    :param rotation: rotation.
    :param size: size of image.
    :returns: plots.
    :rtype: Plots.
    """
    setSize(size)

    if rotation:
        rotation_str = "rotation=90"
    else:
        rotation_str = ""

    options = "Bars [tools=['hover'] {}]".format(rotation_str)

    if not groupby_transform:
        t = lambda x: str(x)
    else:
        t = groupby_transform

    if groupby:
        if not groupby_values:
            groupby_values = df[groupby].unique().tolist()
            groupby_values.sort()

    # Plot the bar
    fields = [x, y, groupby]
    data_df = df[fields].sort_values([y])
    kdims = [(name, titles[name]) for name in [x, y]]

    if not groupby:
        data = [tuple(row) for row in data_df.values]
        bar = hv.Bars(data, kdims[0], kdims[1], label=title)
        plots = [bar.opts(options)]
    else:
        plots = []

        for group in groupby_values:
            group_df = data_df[data_df[groupby] == group]
            data = [tuple(row) for row in group_df.values]
            title_plot = t(group)
            bar = hv.Bars(data, kdims[0], kdims[1], label=title_plot)
            plot = bar.opts(options)
            plots.append(plot)

        plot_layout = hv.Layout(plots).opts(options).cols(num_cols)

        return renderer.get_plot(plot_layout).state


def plot_bar_stack(df, *, x, y, titles, groupby, groupby_values,
                   groupby_transform, rotation, hue=None, hue_values=[], size,
                   num_cols=1, **options):
    """Plot the dataframes as bar plots.

    :param df: dataframe.
    :param titles: dictionary that related the dimension with its name.
    :param x: axis to show.
    :param y: variable to show.
    :param groupby: groupby parameter.
    :param rotation: rotation.
    :param size: size of image.
    :returns: plots.
    :rtype: plots
    """
    global renderer

    setSize(size)

    if rotation:
        rotated_str = "rotation=90"
    else:
        rotated_str = ""

    if hue is None:
        raise ValueError("Error:  hue must be defined")

    if not hue_values:
        raise ValueError("Error: hue_value must have values")

    plots_stack = []

    for group in groupby_values:
        filter_df = df[df[groupby] == group].drop(groupby, 1)
        fields = [x, hue, y]
        data_df = filter_df[fields]
        kdims = [(value, titles[value]) for value in fields]
        data = [tuple(row) for row in data_df.values]
        title = groupby_transform(group)
        plot_options = "Bars [tools=['hover'] color_index=1 stack_index=1 show_legend=False {}]".format(rotated_str)
        bar = hv.Bars(data, kdims[:2],  kdims[2], label=title).opts(plot_options)
        plots_stack.append(bar)

    layout_options = "NdOverlay [show_legend=True, legend_position='right']"
    plot_layout = hv.Layout(plots_stack).opts(layout_options).cols(num_cols)
    return renderer.get_plot(plot_layout).state
