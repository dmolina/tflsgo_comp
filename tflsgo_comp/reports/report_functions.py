"""
This file contains the functions used to show figures of convergence for the
benchmark, using the milestones as references.
"""


def create_tables(df, categories, accuracies, dimension=1000):
    return [], {}, {}


def create_figures(df,
                   categories,
                   accuracies,
                   libplot,
                   dimension,
                   mobile=False):
    """
    Create convergence figures.

    The datasets must have the structure:

    algorithm | f1 | f2 | ... | accuracy | dimension)

    :param df: dataframe with the values to compare.
    :param group: dict with for each category list the functions.
    :param categories: categories to compare (sorted).
    :param algs: algorithm list (sorted).
    """
    mean = {col: 'mean' for col in df.columns if col.startswith('F')}
    dim_df = df[df['dimension'] == dimension]
    df = dim_df.groupby(['alg', 'milestone']).agg(mean).reset_index()

    xticks = [0] + accuracies
    # Get the functions to visualize
    funs_str = [col for col in df.columns if col.startswith('F')]

    def fun_to_int(fun):
        return "{:02d}".format(int(fun[1:]))

    if df['milestone'].max() == 100:
        xticks = [x for x in xticks if x == 1 or x >= 5]

    plots = libplot.plot(
        df,
        x='milestone',
        xaxis='Evaluations',
        xticks=xticks,
        y='mean',
        yaxis='Mean Error',
        logy=True,
        show_legend=True,
        hue='alg',
        groupby=funs_str,
        groupby_transform=fun_to_int,
        group_label='Function',
        kind='line',
        size=200,
        scientific_format=True)

    figures = {
        'Convergence Functions with dimension {}'.format(dimension): plots
    }
    return libplot.to_json(figures)
