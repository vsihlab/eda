# General imports
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def get_dataframe_XYZ_pivot_tables(df, data_column,
                                   x_values_column=None,
                                   y_values_column=None,
                                   fill_value=np.nan):
    """
    Returns X, Y, Z dataframes corresponding to a 2D pivot of the
    given dataframe along X, Y. Expects a 2+ level multi-index and/or
    for x_values_column and y_values_column parameters to be given.
    'X' corresponds to pivot table column, and 'Y' to pivot table
    index, so that returned dataframes' .values attributes are
    plottable 2D matrices.

    If dataframe is 2+ level indexed _and_ one or both columns given,
    the indices will be used to determine row/col of data in table,
    but the values in X/Y matrix will utilize the [x/y]_values_column.
    Otherwise, X/Y values will be sorted numerically, although extra
    multi-index levels above two will be retained (in terms of .values,
    equivalent to stacking all 2D sub-dataframes along the y-axis).
    """
    # flatten as pivot_table() handles errors much better than unstack()
    if df.index.nlevels == 1:
        if (x_values_column is None) or (y_values_column is None):
            raise ValueError("plot_dataframe_2d requires either a 2+ level " +
                             "multi-indexed dataframe or both x_- and y_- " +
                             "values_column parameters to be given.")
        excess_index_columns = []
        x_index_column = x_values_column + '_copy'
        y_index_column = y_values_column + '_copy'
        flatdf = df.reset_index()  # just in case index important
        flatdf[x_index_column] = flatdf[x_values_column]
        flatdf[y_index_column] = flatdf[y_values_column]
    else:
        excess_index_columns = list(df.index.names[:-2])
        y_index_column = df.index.names[-2]
        x_index_column = df.index.names[-1]
        flatdf = df.reset_index()
        if x_values_column is None:
            x_values_column = x_index_column + '_copy'
            flatdf[x_values_column] = flatdf[x_index_column]
        if y_values_column is None:
            y_values_column = y_index_column + '_copy'
            flatdf[y_values_column] = flatdf[y_index_column]
    # add back any extra columns above 2d to keep y-axis ordering.
    pivot_index_columns = excess_index_columns + [y_index_column]
    # just quick-check to make sure these calls don't fail:
    flatdf[data_column]
    flatdf[x_values_column]
    flatdf[y_values_column]
    flatdf[pivot_index_columns]
    flatdf[x_index_column]
    pivot_df = flatdf.pivot_table(values=[data_column, x_values_column, y_values_column],
                                  index=pivot_index_columns,
                                  columns=[x_index_column],
                                  aggfunc=lambda x: x.iloc[0],
                                  fill_value=fill_value)
    xvals_df = pivot_df[x_values_column]  # pd.DataFrames in meshgrid()-style 
    yvals_df = pivot_df[y_values_column]
    zvals_df = pivot_df[data_column]
    return xvals_df, yvals_df, zvals_df

def get_dataframe_2d_matrix_and_axes_vecs(df, data_column,
                                          x_values_column=None,
                                          y_values_column=None,
                                          fill_value=np.nan):
    X, Y, Z = get_dataframe_XYZ_pivot_tables(df, data_column,
                                             x_values_column,
                                             y_values_column,
                                             fill_value)
    x_s = X.mean()  # pd.Series w/ALL values spread across rows
    y_s = Y.T.mean()  # TODO: fix special case of non-np.nan fill values
    return x_s.values, y_s.values, Z.values

# helper fcn for labelling axes with nonconsecutive values:
def get_inflection_points(values):
    if len(values) < 2:
        inflection_point_indices = np.arange(len(values))
        inflection_point_values = np.array(values, copy=True)
        return inflection_point_indices, inflection_point_values
    trend_sign = np.sign(values[1] - values[0])
    vals_iterator = enumerate(values)
    last_ind, last_val = next(vals_iterator)  # pop off and add first (ind, val) pair
    inflection_point_indices = [last_ind]
    inflection_point_values = [last_val]
    for ind, val in vals_iterator:
        if np.sign(val - last_val) != trend_sign:
            trend_sign = np.sign(val - last_val)
            inflection_point_indices.append(last_ind)
            inflection_point_values.append(last_val)
        last_ind, last_val = ind, val
    inflection_point_indices.append(ind)  # add last (ind, val) pair, too
    inflection_point_values.append(val)
    inflection_point_indices = np.array(inflection_point_indices)
    inflection_point_values = np.array(inflection_point_values)
    return inflection_point_indices, inflection_point_values

# function to handle making nice axes ticks for imshow()
# consider it a WIP, can add handling for more edge cases,
# e.g. for logarithmic scales or for smarter picking
#      of #s of major ticks for small # of linear pts
def find_nonmonotonic_axes_ticks_by_index(axis_coord_vec):
    axis_coord_vec = np.array(axis_coord_vec, copy=True)
    inflect_indices, inflect_values = \
        get_inflection_points(axis_coord_vec)
    # if 0-1 inflection points, just return those points
    if len(inflect_indices) < 2:
        return inflect_indices, inflect_values, None, None
    # if most points are inflection points, just tick everything
    if len(inflect_indices) > 0.5 * len(axis_coord_vec):
        maj_tick_indices = np.arange(len(axis_coord_vec))
        maj_tick_values = np.array(axis_coord_vec, copy=True)
        return maj_tick_indices, maj_tick_values, None, None
    # if 2 inflection points (linear / monotonic)
    # and >=5 pts, use 5 major ticks
    if (len(inflect_indices) == 2) and len(axis_coord_vec) >= 5:
        maj_tick_indices = np.linspace(0, len(axis_coord_vec) - 1, 5)
        maj_tick_indices = np.trunc(maj_tick_indices).astype(np.int)
        maj_tick_values = axis_coord_vec[maj_tick_indices]
        return maj_tick_indices, maj_tick_values, None, None
    # otherwise
    inflect_values_diffs = np.diff(inflect_values)
    maj_tick_indices = 1.0 * inflect_indices
    maj_tick_values = 1.0 * inflect_values
    min_tick_indices = \
        maj_tick_indices[1:] - 0.5 * np.diff(inflect_indices)
    min_tick_values = \
        maj_tick_values[1:] - 0.5 * np.diff(inflect_values)
    return maj_tick_indices, maj_tick_values, \
            min_tick_indices, min_tick_values

# def find_nonmonotonic_axes_ticks_on_linear_range(axis_coord_vec):
#     ticks = find_nonmonotonic_axes_ticks_by_index(axis_coord_vec)
#     if ticks is None:
#         return None
#     maj_tick_indices, maj_tick_values, \
#         min_tick_indices, min_tick_values = ticks
#     xmax = max(axis_coord_vec)
#     xmin = min(axis_coord_vec)
#     xrange = xmax - xmin
#     indrange = len(axis_coord_vec)
#     maj_tick_coords = xmin + 1.0 * maj_tick_indices * xrange / indrange
#     min_tick_coords = xmin + 1.0 * min_tick_indices * xrange / indrange
#     return maj_tick_coords, maj_tick_values, \
#             min_tick_coords, min_tick_values

def plot_dataframe_waterfall(df, data_column,
                             num_waterfall_plots=None,
                             x_values_column=None, y_values_column=None,
                             fill_value=np.nan,
                             xlabel=None, ylabel=None,
                             ax=None, add_legend=True,
                             **plot_kwargs):
    xvec, yvec, Zmat = \
        get_dataframe_2d_matrix_and_axes_vecs(df, data_column,
                                              x_values_column,
                                              y_values_column,
                                              fill_value)
    if x_values_column is None:  # disregard original indices
        xvec = np.arange(len(xvec))
    if y_values_column is None:
        yvec = np.arange(len(yvec))
    if num_waterfall_plots is None:  # default 5 plots
        num_waterfall_plots = 5
    num_waterfall_plots = np.array(num_waterfall_plots)
    if num_waterfall_plots.size > 1:
        waterfall_indices = num_waterfall_plots
    else:
        num_waterfall_plots = min(num_waterfall_plots, len(yvec))
        waterfall_indices = np.linspace(0, len(yvec) - 1,
                                        num_waterfall_plots)
    waterfall_indices = np.int64(np.trunc(waterfall_indices))
    z_offset = 0
    for y_ind in waterfall_indices:
        zvals = Zmat[y_ind, :]
        valid_indices = ~np.isnan(zvals)
        zvals = zvals[valid_indices]
        zvals -= zvals.max()
        ax.plot(xvec[valid_indices], zvals + z_offset,
                'd-', label=str(yvec[y_ind]),
                **plot_kwargs)
        z_offset += zvals.min()
    if add_legend:
        if len(waterfall_indices) < 10:
            ax.legend()
        else:
            print('large # plots in waterfall, legend ' +
                  'omitted to avoid overflow.')
    if xlabel is not None:
        ax.set_xlabel(xlabel)
    if ylabel is not None:
        ax.set_ylabel(ylabel)

def plot_matrix_colorplot(matrix, xvec=None, yvec=None,
                          xlabel=None, ylabel=None,
                          ax=None, **imshow_kwargs):
    ny, nx = matrix.shape
    if xvec is None:
        xvec = np.arange(nx)
    if yvec is None:
        yvec = np.arange(ny)
    assert len(xvec) == nx
    assert len(yvec) == ny
    if ax is None:
        plt.figure()
        ax = plt.subplot(111)
    if 'origin' not in imshow_kwargs.keys():
        imshow_kwargs['origin'] = 'upper'
#    'EXTENT' ISSUES: creates coords for axes, but not
#      really useful for anything besides linear ranges
#      e.g. can't handle non-monotonic or nonlinear axes
#    SOLUTION: 
#      custom major ticks marking inflection points
#      & (?) custom minor ticks showing intermediate values
#     # OLD CODE:
#     if 'extent' not in imshow_kwargs.keys():
#         if imshow_kwargs['origin'] == 'upper':
#             imshow_kwargs['extent'] = [min(xvec), max(xvec),
#                                        max(yvec), min(yvec)]
#         else:
#             imshow_kwargs['extent'] = [min(xvec), max(xvec),
#                                        min(yvec), max(yvec)]
#     width = abs(imshow_kwargs['extent'][1] - imshow_kwargs['extent'][0])
#     height = abs(imshow_kwargs['extent'][3] - imshow_kwargs['extent'][2])
#     if width == 0:
#         raise ValueError("plot_matrix_colorplot: width is zero")
#     elif height == 0:
#         raise ValueError("plot_matrix_colorplot: height is zero")
#     else:
#         natural_aspect_ratio = width / height
    # alternate code: coords are just indices
    imshow_kwargs['extent'] = None
    natural_aspect_ratio = len(xvec)/len(yvec)
    if 'aspect' in imshow_kwargs.keys():
        if imshow_kwargs['aspect'] is not None:
            imshow_kwargs['aspect'] *= natural_aspect_ratio
    if 'cmap' not in imshow_kwargs.keys():
        imshow_kwargs['cmap'] = 'jet'
    if 'interpolation' not in imshow_kwargs.keys():
        imshow_kwargs['interpolation'] = 'nearest'
    ax.imshow(matrix, **imshow_kwargs)
    if xlabel is not None:
        ax.set_xlabel(xlabel)
    if ylabel is not None:
        ax.set_ylabel(ylabel)
    xticks = find_nonmonotonic_axes_ticks_by_index(xvec)
    if xticks is not None:
        ax.xaxis.set_ticks(xticks[0], minor=False)
        ax.xaxis.set_ticklabels(xticks[1], minor=False)
#         ax.xaxis.set_ticks(xticks[2], minor=True)
#         ax.xaxis.set_ticklabels(xticks[3], minor=True, fontsize=14)
    yticks = find_nonmonotonic_axes_ticks_by_index(yvec)
    if yticks is not None:
        ax.yaxis.set_ticks(yticks[0], minor=False)
        ax.yaxis.set_ticklabels(yticks[1], minor=False)
#         ax.yaxis.set_ticks(yticks[2], minor=True)
#         ax.yaxis.set_ticklabels(yticks[3], minor=True, fontsize=14)
#    plt.show()  # screws up other plots subsequent to this one

def plot_dataframe_colorplot(df, data_column,
                             x_values_column=None, y_values_column=None,
                             fill_value=np.nan,
                             xlabel=None, ylabel=None,
                             ax=None, **imshow_kwargs):
    xvec, yvec, Zmat = \
        get_dataframe_2d_matrix_and_axes_vecs(df, data_column,
                                              x_values_column,
                                              y_values_column,
                                              fill_value)
    if x_values_column is None:  # disregard original indices
        xvec = np.arange(len(xvec))
    if y_values_column is None:
        yvec = np.arange(len(yvec))
    plot_matrix_colorplot(Zmat, xvec, yvec,
                          xlabel=xlabel, ylabel=ylabel,
                          ax=ax, **imshow_kwargs)


#     plot_label_column_names = ['wavelength', 'pump_power']
#     plotlabel = "\n".join(['{}: {}'.format(colname, dataframe.loc[run_id][colname].iloc[0])
#                            for colname in plot_label_column_names])
#     ax.text(1.1, 0.9, plotlabel, verticalalignment='top', horizontalalignment='left',
#             transform=ax.transAxes, color='black', fontsize=16)

#     x_tick_label_indices, x_tick_label_values = get_axis_ticks(x_s,
#                                                                use_inflection_points=False)
#     x_tick_labels = ["{}".format(val)
#                      for val in x_tick_label_values]
#     y_tick_label_indices, y_tick_label_values = get_axis_ticks(y_s,
#                                                                use_inflection_points=False)
#     y_tick_labels = ["{}".format(val)
#                      for val in y_tick_label_values]
#     if x_tick_label_indices is not None:
#         plt.xticks(x_tick_label_indices, x_tick_labels)
#     if y_tick_label_indices is not None:
#         plt.yticks(y_tick_label_indices, y_tick_labels)

# def plot_2d_with_run_id_slider(dataframe, data_column,
#                                x_values_column=None, y_values_column=None):
#     """
#     Expects a 3-level-multi-indexed dataframe and a column name corresponding
#     to the value to be plotted. Optionally, columns containing values corresponding
#     to each axis can be provided, otherwise the labels in the dataframe's index
#     will be used.
#     """
#     def plot_2d_by_3rd_index(dataframe, third_index):
#         plot_dataframe_2d(dataframe.xs(third_index, level=-3), 
#                           data_column, x_values_column, y_values_column)

#     run_id_slider = widgets.IntSlider(min=0, max=dataframe.index.get_level_values('run_id').max(),
#                                       value=0, description='Run ID:')
#     widgets.interact(plot_2d_by_3rd_index, dataframe=widgets.fixed(dataframe), run_id=run_id_slider);
