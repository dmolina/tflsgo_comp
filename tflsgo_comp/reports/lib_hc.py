"""
This file contains the wrapper for the plot API using the HighCharts
libraries. https://www.highcharts.com/products/highcharts/
It is free for non-commercial usage
"""
from pandas_highcharts.core import serialize
from highcharts import highcharts
import json

def additional_options(chart_dict, scientific_format):
    chart_dict.update()

    if scientific_format:
        ayis_sci_format_str = highcharts.common.Formatter("function() { if (this.value < 1e-40) {return '0.0';}; return this.value.toExponential(2);}")
        axis_sci_format_str = highcharts.common.Formatter("function() { return this.value.toExponential(2);}")
        axis_format = [axis_sci_format_str, ayis_sci_format_str]
        tooltip_sci_format_str = highcharts.common.Formatter("function() {return this.y.toExponential(2);}")

        for axis_name, formatter in zip(["xAxis", "yAxis"], axis_format):

            if axis_name in chart_dict:
                label = dict()
                xaxis = chart_dict[axis_name]

                if type(xaxis) is list:
                    print(xaxis)
                    xaxis = xaxis[0]
                    print(xaxis)

                label = xaxis.get('labels', dict())
                print(label)
                label['formatter'] = formatter
                xaxis['labels'] = label
                chart_dict[axis_name] = xaxis
                print(chart_dict[axis_name])

        tooltip = chart_dict.get("tooltip", dict())
        tooltip['formatter'] = tooltip_sci_format_str
        chart_dict['tooltip'] = tooltip

    # print(chart_dict)
    str = json.dumps(chart_dict, cls=highcharts.highcharts.HighchartsEncoder)
    print(str)
    return str


def is_set_title():
    return False

def plot(df, x, y, label=None, xticks=None, xaxis=None, yaxis=None, logy=False,
         show_legend=True, groupby=None, group_label='',
         groupby_transform=None, hue=None, cols=1, kind='line', size=None,
         scientific_format=False):
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

            if logy:
                y_max = int(group_df.max(1).max())
                y_min = int(group_df.min(1).min())

                if y_min < 1e-40:
                    group_df = group_df.clip(lower=1e-40)
                    y_min = 1e-40
                params.update(dict(ylim=[y_min,y_max]))

            dst = 'figures{}'.format(i+1)
            title = "{}: {:02d}".format(group_label, groupby_transform(group))
            chart_options = serialize(group_df, title=title, output_type='dict', **params, render_to=dst)
            plot = additional_options(chart_options, scientific_format)
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
