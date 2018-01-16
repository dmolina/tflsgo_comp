from bokeh.embed import components
import importlib

import holoviews as hv
hv.extension('bokeh')


def load_charts_library(lib='hv'):
    libs = ['hv', 'hc']

    if lib not in libs:
        raise ValueError("Library '{}' unknown".format(lib))

    lib_name = "reports.lib_{}".format(lib)
    library = importlib.import_module(lib_name, __name__)
    return library


def figure_json(fig_names, plots, libcharts='hv'):
    """Make the figure visualize with the json.

    :param fig_names: name of the figs
    :param plots: plots to visualize
    :param libcharts: type of plot library (hv is currently only supported)
    :returns: dictionary of type
    :rtype: {'error': ...,'plots': [{'title': .., 'js': ..,  'tags': ..}, ..]}
    """
    result = dict()
    error = ''
    script, divs = components(plots, wrap_script=False)
    result['js'] = script
    result['divs'] = divs

    result.update({'error': error, 'type': 'hv'})
    return result


def get_plot_bar(data_df, title):
    """Return a bar plot with the data and the title

    :param data_df: dataframe with the data.
    :param title: title for the plot.
    :returns: A plot (bokeh plot).
    :rtype: bokeh plot.
    """
    # Prepare to visualize
    kdims = [('alg', 'Algorithm'), ('Value', 'Ranking')]
    # Plot the bar
    bar = hv.Bars(data_df, kdims[0], kdims[1], label=title)
    options = "Bars [tools=['hover']]"
    return bar.opts(options)


def getfilter_category(category):
    """Get the string to filter the functions.

    :param category: category to filter.
    :returns: string with the name of functions to filter using it.
    :rtype: str

    """
    # Filter only the function in the category
    cat_funs = [x for x in category['functions'].split(',')]
    functions = ['F{}'.format(x) for x in cat_funs]
    return functions


def filter_milestone(df, milestone_name):
    """Filter by the milestone.

    Because the milestone could be in other format, this function is required.

    :param df: dataset.
    :param milestone_name: milestone name
    :returns: DataFrame filtering by the milestone
    :rtype: DataFrame

    """
    milestone_value = int(float(milestone_name))
    # Filter the milestone
    cat_df_mil = df[df['milestone'].astype(int) == milestone_value]
    return cat_df_mil
