# General imports
import textwrap

from IPython.display import display
from ipywidgets import fixed, interactive, IntSlider
from lmfit import report_fit
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import eda.analysis.dataframe_processing as dfproc

def colorstr_generator():
    ind = 0
    while True:
        ind += 1
        yield 'C' + str(ind % 10)

def arrowplot(xvals, yvals, colorstr, ax,
              width=1.5, headwidth=7.5, headlength=7.5,
              skip_inds=None, **plot_kwargs):
    ax.plot(xvals, yvals, colorstr + '-', **plot_kwargs)
    lastxval, lastyval = None, None
    for ind, (xval, yval) in enumerate(zip(xvals, yvals)):
        if skip_inds is not None:
            if ind in skip_inds:
                lastxval = None
        if lastxval is not None:
            ax.annotate("", xy=(xval, yval),
                        xytext=(lastxval, lastyval),
                        arrowprops=dict(width=width, fc=colorstr,
                                        headwidth=headwidth,
                                        headlength=headlength))
        lastxval, lastyval = xval, yval

def get_dataframe_XYZ_pivot_tables(df, data_column,
                                   x_values_column=None,
                                   y_values_column=None,
                                   fill_value=np.nan):
    """
    Pivots dataframe around rightmost multi-index, or around x_values
    if dataframe is single-index, with the value given by data_column.
    Y ordering is determined by remaining multi-index cols, equivalent
    to stacking all 2D sub-dataframes along the y-axis, or y_values
    if dataframe is single-index.

    Values of 3 pivoted dataframes are x_values column values
    (or rightmost index), y_values column values (or 2nd-to-rightmost index),
    then data_column values, respectively, of the original dataframe rows
    that correspond to each new (x, y) coordinate.

    WARNING: Setting the fill_value to anything but np.nan may have
    unintended consequences for X and Y, for reasons unknown
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
                                          fill_value=np.nan,
                                          force_no_xvals_conflicts=False):
    """
    Pivots dataframe around rightmost multi-index, or around x_values
    if dataframe is single-index, with the value given by data_column.
    Y ordering is determined by remaining multi-index cols, equivalent
    to stacking all 2D sub-dataframes along the y-axis, or y_values
    if dataframe is single-index. Values of returned dataframe are given
    by the data_column value of each row in original dataframe.

    Furthermore, uses [x/y]_values_column to return the coordinate arrays
    along each axis, even if they are non-linear or unsorted. If not
    given, index values are used instead.

    Parameter force_no_xvals_conflicts is for cases where there is not
    a unique x-value for each x-index (rightmost multi-index level).
    e.g.          x-value   y-value  ...
         (0, 0) |       0        10  ...
         (0, 1) |       1      11.5  ...
         (1, 0) |     0.5        12  ...
         (1, 1) |     1.5      12.5  ...
    This is accomplished by making all x-indices unique, effectively
    turning X and Z pivot tables into a diagonal block matrix so as
    to give unique values for each column and thus x-vector.
        force_no_xvals_conflicts=False, same xvals per x-index:
                   0     1
            0 |  0.0   1.0    ->   x-vector: (0, 1)
            1 |  0.0   1.0
        force_no_xvals_conflicts=False, different xvals per x-index:
                   0     1
            0 |  0.0   1.0    ->   x-vector: (0.25, 1.25)
            1 |  0.5   1.5
        force_no_xvals_conflicts=True, different xvals per x-index:
                 0,0   0,1   1,0   1,1
            0 |  0.0   1.0   NaN   NaN ->   x-vector:
            1 |  NaN   NaN   0.5   1.5      (0, 1, 0.5, 1.5)

    This also turns Z into a diagonal block matrix, meaning this
    option is _not_ reccomended for colorplots!

    WARNING: Setting the fill_value to anything but np.nan may have
    unintended consequences for X and Y, for reasons unknown
    """
    X, Y, Z = get_dataframe_XYZ_pivot_tables(df, data_column,
                                             x_values_column,
                                             y_values_column,
                                             fill_value)
    xval_stds = X[df.index.get_level_values(-1).unique()].std()
    xval_stds.fillna(0, inplace=True)
    have_xval_conflicts = np.logical_or.reduce(xval_stds.values > 0)
    if force_no_xvals_conflicts and have_xval_conflicts:
        both_index_levels = list(range(df.index.nlevels))
        both_level_names = list(np.array(df.index.names)[both_index_levels])
        both_level_names_str = ', '.join(both_level_names)
        dummy_index_format_str = \
            ', '.join(('{0[' + str(level) + ']:09.03f}')
                      for level in both_index_levels)
        new_index = [df.index.get_level_values(-2),
                     df.index.map(dummy_index_format_str.format)]
        new_df = df.reset_index(level=both_index_levels, drop=True)
        new_df.index = new_index
        new_df.index.set_names(both_level_names_str, level=-1, inplace=True)
        X, Y, Z = get_dataframe_XYZ_pivot_tables(new_df, data_column,
                                                 x_values_column,
                                                 y_values_column,
                                                 fill_value)
    # TODO: also fix yvals
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
        if max(abs(maj_tick_values)) > 10:
            maj_tick_values = np.round(maj_tick_values).astype(np.int)
        return maj_tick_indices, maj_tick_values, None, None
    # if 2 inflection points (linear / monotonic)
    # and >=6 pts, use 6 major ticks
    if (len(inflect_indices) == 2) and len(axis_coord_vec) >= 6:
        maj_tick_indices = np.linspace(0, len(axis_coord_vec) - 1, 6)
        maj_tick_indices = np.trunc(maj_tick_indices).astype(np.int)
        maj_tick_values = axis_coord_vec[maj_tick_indices]
        if max(abs(maj_tick_values)) > 10:
            maj_tick_values = np.round(maj_tick_values).astype(np.int)
        return maj_tick_indices, maj_tick_values, None, None
    # otherwise
    inflect_values_diffs = np.diff(inflect_values)
    maj_tick_indices = 1.0 * inflect_indices
    maj_tick_values = 1.0 * inflect_values
    if max(abs(maj_tick_values)) > 10:
        maj_tick_values = np.round(maj_tick_values).astype(np.int)
    min_tick_indices = \
        maj_tick_indices[1:] - 0.5 * np.diff(inflect_indices)
    min_tick_values = \
        maj_tick_values[1:] - 0.5 * np.diff(inflect_values)
    if max(abs(min_tick_values)) > 10:
        min_tick_values = np.round(min_tick_values).astype(np.int)
    return maj_tick_indices, maj_tick_values, \
            min_tick_indices, min_tick_values

def plot_dataframe_waterfall(df, data_column,
                             num_waterfall_plots=None,
                             x_values_column=None, y_values_column=None,
                             fill_value=np.nan,
                             xlabel=None, ylabel=None,
                             ax=None, add_legend=True,
                             use_arrowplot=False,
                             arrow_width=1.0,
                             arrow_headwidth=5.0,
                             arrow_headlength=5.0,
                             **plot_kwargs):
    df2d, _ = dfproc.get_2d_indexed_df(df)
    xvec, yvec, Zmat = \
        get_dataframe_2d_matrix_and_axes_vecs(df2d,
                                              data_column,
                                              x_values_column,
                                              y_values_column,
                                              fill_value,
                                              force_no_xvals_conflicts=True)
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
        if num_waterfall_plots <= 0:  # 0 or negative is max # plots
            num_waterfall_plots = len(yvec)
        waterfall_indices = np.linspace(0, len(yvec) - 1,
                                        num_waterfall_plots)
    waterfall_indices = np.array(np.trunc(waterfall_indices),
                                 dtype=np.int)
    z_offset = 0
    colorgen = colorstr_generator()
    for y_ind in waterfall_indices:
        zvals = Zmat[y_ind, :]
        valid_indices = ~np.isnan(zvals)
        zvals = zvals[valid_indices]
        zvals -= zvals.max()
        if use_arrowplot:
            arrowplot(xvec[valid_indices], zvals + z_offset,
                      next(colorgen), ax, 
                      width=arrow_width,
                      headwidth=arrow_headwidth,
                      headlength=arrow_headlength,
                      **plot_kwargs)
        else:
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
    imshow_kwargs = imshow_kwargs.copy()
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
    """
    [docstring not yet completed]
    if df index is not a multi-index, [x & y]_values_column are needed,
        and pivot is performed based on those values if possible.
        Those values are used for coordinate ticks.
    if df index is a multi-index, pivot is based on rightmost two
        indices of multi-index, but [x/y]_values_column are used for
        coordinate ticks, even if unsorted/nonlinear.

    Either way, data_column entries of each source row corresponding
    to each pivoted (x, y) element are used to create the
    "Z" (color) values.
    """
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


def print_indices(df, last_index=None, column_width=80):
    """
    Prints in a somewhat readable manner every high-level
    index and its sub-indices, either through all indices
    or stopping short at some level.
    """
    num_index_levels = df.index.nlevels
    levels_list = list(range(-num_index_levels, -1))
    first_1d_val_df = df.groupby(level=levels_list).head(1)
    def print_subtree(df, tab_level=0, prefix=""):
        levels_list = list(range(df.index.nlevels))
        index_vals_obj = df.index.get_level_values(0).unique()
        index_name = index_vals_obj.name
        if index_name is None:
            return
        index_vals_str = ", ".join(str(val) for val in index_vals_obj.values)
        indent = "    " * tab_level
        bigindent = indent + "    "
        wrapper = textwrap.TextWrapper(column_width - len(indent),
                                       bigindent, bigindent)
        index_vals_str = wrapper.fill(index_vals_str)
        print(indent + "all values for index '{}': \n{}".format(
                index_name, index_vals_str))
        if len(levels_list) > 1:
            if last_index:
                if df.index.nlevels <= -1 * last_index:
                    return
            for val in index_vals_obj:
                index_str = prefix
                if index_str:
                    index_str += ", "
                index_str += '{} = {}'.format(index_name, val)
                print(indent + "[{}]".format(index_str))
                sub_df = df.loc[val]
                print_subtree(sub_df, tab_level + 1, index_str)
    print_subtree(df)


# Consider this a "beta" version, subject to change!
def display_data(
                 # shared requirements / general settings
                 df, file_metadata_list, data_column,
                 x_vals_column=None, coord_2d_column=None,
                 x_vals_label=None, coord_2d_label=None,
                 figsize_scale=1.0, font_scale=1.0,
                 # 2d colorplot / waterfall
                 display_2d_colorplot=False, imshow_kwargs=None,
                 display_waterfall=False, num_waterfall_plots=4,
                 display_2d_save_filepath=None,
                 # requirements for fit analysis plots
                 results_df=None, minimize_results=None,
                 fit_function=None, 
                 # display all fits at once or w/ widget
                 display_fits=None, num_fit_plots_cols=3,
                 residuals_fcn=None, indep_vars_columns=None,
                 display_fits_save_filepath=None,
                 # display fit params (and more) 
                 display_fit_results=None,
                 num_result_plots_cols=3,
                 other_results_list=['chisqr'],
                 display_fit_results_save_filepath=None,
                 # display covariance / correlations matrix
                 display_covar=None,
                 display_covar_save_filepath=None,
                 # display detailed fit reports
                 display_fit_reports=False):
    """
    [docstring not yet completed]
    PARAM display_fits options:
        None: no fits displayed
        'all': show all fits, using num_fit_cols
               for layout
        'widget': use widget to change current fit

    PARAM display_fit_results:
        Display columns from results_df as lines,
        vs first index of results_df, with separate
        lines for each second index of results_df.
        errorbars are used if param/attribute has a
        "[name]_error" column.
    display_fit_results options:
        None: no results displayed
        'params': display all fit parameters
        [list of strings]: display these results_df cols

    PARAM other_results_list: add these to params
        or list of strings from display_fit_results

    PARAM display_covar options:
        None: no matrices displayed
        'covariance': avg. covariance matrix
        'correlation': avg. correlation matrix
    """
    # PLOT 2D REPRESENTATION
    if not (display_2d_colorplot or display_waterfall):
        pass
    elif display_2d_colorplot and display_waterfall:
        plt.figure(figsize=(figsize_scale * 4,
                            figsize_scale * 2))
        nplots = 2
    else:  # xor
        plt.figure(figsize=(figsize_scale * 2.5,
                            figsize_scale * 2.5))
        nplots = 1
    if imshow_kwargs is None:
        imshow_kwargs = {'aspect': 1.0,
                         'origin': 'upper'}
    if display_2d_colorplot:
        ax1 = plt.subplot(1, nplots, 1)
        plot_dataframe_colorplot(df, data_column,
                                 x_vals_column, coord_2d_column,
                                 xlabel=x_vals_label, ylabel=coord_2d_label,
                                 ax=ax1, **imshow_kwargs)
    if display_waterfall:
        plotnum = 2 if display_2d_colorplot else 1
        ylabel = None if display_2d_colorplot else coord_2d_label
        ax2 = plt.subplot(1, nplots, plotnum)
        plot_dataframe_waterfall(df, data_column,
                                 num_waterfall_plots,
                                 x_vals_column, coord_2d_column,
                                 xlabel=x_vals_label, ylabel=ylabel, ax=ax2)
        ax2.yaxis.set_ticklabels([])
    if (display_2d_colorplot or display_waterfall) \
            and display_2d_save_filepath:
        plt.savefig(display_2d_save_filepath,
                    bbox_inches='tight', transparent=False)
    if display_2d_colorplot or display_waterfall:
        plt.show()

    # plot fit results if given
    if results_df is None or minimize_results is None:
        return

    # plot fits
    if (display_fits == 'all' or display_fits == 'widget') \
            and (indep_vars_columns and residuals_fcn):
        if x_vals_column is None:
            x_vals_column = df.index.names[-1]
        def plot_fit(result_index, axes=None):
            if axes:
                ax = axes
            else:
                plt.figure(figsize=(figsize_scale * 3,
                                    figsize_scale * 3))
                ax = plt.subplot(111)
            result = minimize_results[result_index]
            dataset_index = results_df.index[result_index]
            xvals = df.loc[dataset_index][x_vals_column]
            yvals = df.loc[dataset_index][data_column]
            indep_vars_vecs = [df.loc[dataset_index][colname]
                               for colname in indep_vars_columns]
            fit_yvals = residuals_fcn(result.params, *indep_vars_vecs)
            ax.plot(xvals, yvals, 'bd', label='dataset {}'.format(result_index))
            ax.plot(xvals, fit_yvals, 'r')
            if axes is None:
                plt.show()
        if display_fits_save_filepath or display_fits == 'all':
            ncols = num_fit_plots_cols
            nplots = len(minimize_results)
            nrows = np.int(np.ceil(nplots / ncols))
            plt.figure(figsize=(figsize_scale * 1.5 * min(ncols, 5),
                                figsize_scale * 1.3 * nrows))
            for result_index in list(range(nplots)):
                ax = plt.subplot(nrows, ncols, result_index + 1)
                plot_fit(result_index, ax)
            plt.tight_layout()
            if display_fits_save_filepath:
                plt.savefig(display_fits_save_filepath,
                            bbox_inches='tight', transparent=False)
            if display_fits == 'all':
                plt.show()
            else:
                plt.close()
        if display_fits == 'widget':
            result_slider = IntSlider(min=0, max=len(minimize_results) - 1,
                                      step=1, value=0)
            interactive_plot = interactive(plot_fit,
                                           result_index=result_slider,
                                           axes=fixed(None)) 
            # Note: axes=fixed(None) was once in those params, not sure why
            output = interactive_plot.children[-1]
            output.layout.height = '350px'
            display(interactive_plot)
            interactive_plot.update()
    elif not display_fits:  # False or None
        pass
    else:
        raise ValueError("Invalid value for keyword argument display_fits")

    # plot params, grouped by all but last column
    if display_fit_results:
        results_df_2d, _ = dfproc.get_2d_indexed_df(results_df)
        result = minimize_results[0]
        if display_fit_results == 'params':
            params_to_plot_list = list(result.var_names)
        else:
            try:
                test_iterator = iter(display_fit_results)
            except TypeError:  # not iterable
                raise ValueError("Invalid value for keyword " +
                                 "argument display_fit_results")
            else:
                params_to_plot_list = list(test_iterator)
        params_to_plot_list += list(other_results_list)
        ncols = num_result_plots_cols
        nplots = len(params_to_plot_list)
        nrows = np.int(np.ceil(nplots / ncols))
        plt.figure(figsize=(figsize_scale * 1.5 * min(ncols, 6),
                            figsize_scale * 1.3 * nrows))
        for ind, param in enumerate(params_to_plot_list):
            ax = plt.subplot(nrows, ncols, ind + 1)
            indices_2d = results_df_2d.index.get_level_values(-2).unique()
            for index_2d in indices_2d:
                subdf = results_df_2d.loc[index_2d]
                if (param + '_error') in list(results_df_2d):
                    ax.errorbar(x=subdf.index.get_level_values(-1),
                                y=subdf[param],
                                yerr=subdf[param + '_error'],
                                fmt='d-', label=index_2d)
                else:
                    ax.plot(subdf.index.get_level_values(-1),
                            subdf[param].values, 'd-', label=index_2d)
            if len(indices_2d) <= 5:
                plt.legend()
            plt.xlabel(results_df_2d.index.names[-1])
            plt.tight_layout()
            plt.title(param)
        if display_fit_results_save_filepath:
            plt.savefig(display_fit_results_save_filepath,
                        bbox_inches='tight', transparent=False)
        plt.show()

    # Plot the avg. covariance matrix
    if (display_covar == 'covariance' or
            display_covar == 'correlation'):
        covar_mats = []
        corr_mats = []
        for result in minimize_results:
            covar = result.covar
            covar_mats.append(covar)
            if display_covar == 'correlation':
                oostd = np.diagflat(
                    [1.0 / param.stderr
                     for param in list(result.params.values())
                     if param.name in result.var_names
                     if param.stderr != 0])
                corr = np.dot(np.dot(oostd, result.covar),
                              oostd).astype(np.float)
                mask = np.zeros_like(corr, dtype=np.bool)
                mask[np.triu_indices_from(mask)] = True
                corr[mask] = np.nan
                corr_mats.append(corr)

        # filter out malformed covariance / correlation matrices
        if display_covar == 'covariance':
            valid_mats = [mat for mat in covar_mats
                          if mat.size is not None
                          if mat.size > 0]
        else:
            valid_mats = [mat for mat in corr_mats
                          if mat.size is not None
                          if mat.size > 0]
        num_nan = lambda mat: np.count_nonzero(np.isnan(mat))
        avg_nan = np.mean([num_nan(mat) for mat in valid_mats])
        avgcorr = np.mean([mat for mat in valid_mats
                           if num_nan(mat) <= avg_nan], axis=0)

        plt.figure()
        plt.imshow(avgcorr, vmin=-1, vmax=1)
        plt.colorbar()
        plt.xticks(np.arange(result.nvarys), result.var_names,
                   rotation=-35, ha='left')
        plt.yticks(np.arange(result.nvarys), result.var_names)
        plt.title('Avg. correlation matrix, off-diagonal')
        if display_covar_save_filepath:
            plt.savefig(display_covar_save_filepath,
                        bbox_inches='tight', transparent=False)
        plt.show()
    elif not display_covar:  # False or None
        pass
    else:
        raise ValueError("Invalid value for keyword argument display_covar")

    # DETAILED FIT REPORTS
    if display_fit_reports:
        for result_index, result in enumerate(minimize_results):
            print('----------------------------------------')
            if (display_covar == 'covariance' or
                    display_covar == 'correlation') \
                    and (indep_vars_columns and residuals_fcn):
                fig, (ax1, ax2) = plt.subplots(
                    ncols=2, sharey=False, figsize=(figsize_scale * 4.0,
                                                    figsize_scale * 1.5))
            elif (display_covar == 'covariance' or
                    display_covar == 'correlation') \
                    or (indep_vars_columns and residuals_fcn):
                fig = plt.figure(figsize=(figsize_scale * 2.0,
                                          figsize_scale * 1.0))
                ax1 = plt.subplot(111)
                ax2 = ax1  # either alias points to same fig
            if indep_vars_columns and residuals_fcn:
                dataset_index = results_df.index[result_index]
                xvals = df.loc[dataset_index][x_vals_column]
                yvals = df.loc[dataset_index][data_column]
                indep_vars_vecs = [df.loc[dataset_index][colname]
                                   for colname in indep_vars_columns]
                fit_yvals = residuals_fcn(result.params, *indep_vars_vecs)
                ax1.plot(xvals, yvals, 'bd',
                         label='dataset {}'.format(result_index))
                ax1.plot(xvals, fit_yvals, 'r')
                ax1.set_title('Data vs. Fit')
            if (display_covar == 'covariance' or
                    display_covar == 'correlation'):
                if display_covar == 'correlation':
                    mat = corr_mats[result_index]
                else:
                    mat = covar_mats[result_index]
                if mat.size is not None and mat.size > 0:
                    img = ax2.imshow(mat, vmin=-1, vmax=1)
                    fig.colorbar(img, ax=ax2)
                    plt.xticks(np.arange(result.nvarys), result.var_names,
                               rotation=-35, ha='left', fontsize=font_scale*8)
                    plt.yticks(np.arange(result.nvarys), result.var_names,
                               fontsize=font_scale*8)
                    ax2.set_title('Correlations')
            plt.tight_layout()
            plt.show()
            print('FIT #{}'.format(result_index + 1))
            for col, val in zip(results_df.index.names,
                                results_df.index[result_index]):
                print('{}: {}'.format(col, val))
            display(report_fit(result))

# CURRENTLY UNUSED CODE SNIPPETS
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
#
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
