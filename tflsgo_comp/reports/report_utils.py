import holoviews as hv
hv.extension('bokeh')


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
