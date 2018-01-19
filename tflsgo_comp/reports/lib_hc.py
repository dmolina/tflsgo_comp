"""
This file contains the wrapper for the plot API using the HighCharts
libraries. https://www.highcharts.com/products/highcharts/
It is free for non-commercial usage
"""
import pandas as pd
from pandas_highcharts.core import serialize
from highcharts import highcharts
import json

num_plot = 0


def init():
    global num_plot
    num_plot = 0


def next_plot():
    global num_plot
    num_plot += 1
    return "figures{}".format(num_plot)


def additional_options(chart_dict, scientific_format=False,
                       label_display=False, isRatio=False):
    chart_dict.update()

    if scientific_format:
        ayis_sci_format_str = highcharts.common.Formatter("function() { if (this.value < 1e-40) {return '0.0';}; return this.value.toExponential(2);}")

        if isRatio:
            axis_sci_format_str = highcharts.common.Formatter("function() { return this.value.toFixed(0)+'%';}")
        else:
            axis_sci_format_str = highcharts.common.Formatter("function() { return this.value.toExponential(2);}")

        axis_format = [axis_sci_format_str, ayis_sci_format_str]
        tooltip_sci_format_str = highcharts.common.Formatter("function() {return this.y.toExponential(2);}")

        for axis_name, formatter in zip(["xAxis", "yAxis"], axis_format):

            if axis_name in chart_dict:
                label = dict()
                xaxis = chart_dict[axis_name]

                if type(xaxis) is list:
                    xaxis = xaxis[0]

                label = xaxis.get('labels', dict())
                label['formatter'] = formatter
                xaxis['labels'] = label
                chart_dict[axis_name] = xaxis

        tooltip = chart_dict.get("tooltip", dict())
        tooltip['formatter'] = tooltip_sci_format_str
        chart_dict['tooltip'] = tooltip

    if label_display:
        plotOptions = chart_dict.get("plotOptions", dict())
        plotOptions['line'] = dict(dataLabels=dict(enabled=highcharts.common.Formatter("true")))
        chart_dict['plotOptions'] = plotOptions

    # print(chart_dict)
    str = json.dumps(chart_dict, cls=highcharts.highcharts.HighchartsEncoder)
    # print(str)
    return str


def plot(df, x, y, label=None, xticks=None, xaxis=None, yaxis=None, logy=False,
         show_legend=True, groupby=None, group_label='',
         groupby_transform=None, hue=None, cols=1, kind='line', size=None,
         scientific_format=False):
    params = dict(figsize=size, zoom="xy", logy=logy)
    isRatio = df[x].max() == 100

    if xticks:
        params.update(dict(xticks=xticks))

    if groupby is None and label is None:
        error = "label is mandatory without groupby"
        raise ValueError(error)

    if xaxis is None:
        xaxis = x.title()

    if yaxis is None:
        yaxis = y.title()

    if isRatio:
        xaxis = '{} (%)'.format(xaxis)

    params = dict(show_legend=show_legend, logy=logy)

    if xticks:
        params.update({'xticks': xticks})

    if groupby is None:
        return [serialize.plot_elem(df, y=y, **params)]
    else:
        if type(groupby) is not list:
            groupby = ["{}".format(groupby)]

        plot_df = df.pivot(index=x, columns=hue)
        plots = []

        for group in groupby:
            group_df = plot_df[group]
            group_df.index.names = [xaxis]

            if logy:
                # y_max = int(group_df.max(1).max())
                y_min = int(group_df.min(1).min())

                if y_min < 1e-40:
                    group_df = group_df.clip(lower=1e-40)
                    y_min = 1e-40
                    # params.update(dict(ylim=[y_min,y_max]))

            title = "{}: {}".format(group_label, groupby_transform(group))
            chart_options = serialize(group_df, title=title,
                                      output_type='dict', **params,
                                      render_to=next_plot())
            plot = additional_options(chart_options, scientific_format=True,
                                      isRatio=isRatio, label_display=False)
            plots.append(plot)

        return plots


def plot_bar(df, titles, x, y, groupby=None, groupby_values=None,
             groupby_transform=None, rotation=False, size=None, title=None,
             num_cols=3, scientific_format=False):
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
    # import ipdb; ipdb.set_trace()
    params = dict(zoom="xy", kind='bar', legend=False)

    if size:
        params.update(dict(figsize=size))

    if not groupby_transform:
        t = lambda x: str(x)
    else:
        t = groupby_transform

    if groupby:
        if not groupby_values:
            groupby_values = df[groupby].unique().tolist()
            groupby_values.sort()

    if not groupby:
        plot_df = df[[x, y]]
        chart_options = serialize(plot_df, title=title, output_type='dict', **params, render_to=next_plot())
        plot = additional_options(chart_options, scientific_format, label_display=True)
        plots = [plot]
    else:
        plots = []

        for group in groupby_values:
            group_df = df[df[groupby] == group]
            plot_df = group_df[[x, y]]
            plot_df[y] = pd.to_numeric(plot_df[y])
            plot_df.columns = [titles[v] for v in plot_df.columns]
            title = t(group)
            plot_df = plot_df.set_index(titles[x])

            chart_options = serialize(plot_df, title=title, output_type='dict',
                                      **params, render_to=next_plot())
            plot = additional_options(chart_options, scientific_format,
                                      label_display=True)
            plots.append(plot)

    return plots


# From https://codereview.stackexchange.com/questions/178600/flatten-an-array-of-integers-in-python
def flatten_list(array):
    for element in array:
        if isinstance(element, str):
            yield element
        elif isinstance(element, list):
            yield from flatten_list(element)
        else:
            raise TypeError("Unsupported type ({})".format(
                type(element).__name__))


def is_lineal(plots):
    """Detect if a list of plot is lineal.

    :param plots: plots to observ.
    :returns: True if it is lineal (like Convergence)
    :rtype: False othercase.

    """
    if plots:
        key_first = list(plots.keys())[0]
        first = plots[key_first]
        return type(first[0]) is str
    else:
        return False


def to_json(plots, title=None):
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
    plots_json = []
    plots_js = []

    # If it is not a double-array it is transformed as a double-array
    lineal = is_lineal(plots)

    if lineal:
        for key, plots_seq in plots.items():
            plots[key] = [[p] for p in plots_seq]

    if plots:
        for title, plots_col in plots.items():

            for plots_row in plots_col:
                plots_json.append({'title': title, 'num': len(plots_row)})
                title = ''
                plots_js.extend(plots_row)

    result.update({'figures_info': plots_json})
    result.update({'figures': plots_js})
    result.update({'error': error, 'type': 'highcharts'})
    return result
