# ----------------------------------------------------------------------------
# Copyright (c) 2024, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import rpy2.robjects as ro
from rpy2.robjects.methods import RS4
from rpy2.robjects.packages import importr
from rpy2.robjects import pandas2ri

from typing import Optional
from pathlib import Path

from q2_qsip2.visualizers._helpers import _ggplot2_object_to_visualization

qsip2 = importr('qSIP2')


def plot_weighted_average_densities(
    output_dir: str, qsip_data: RS4, group: Optional[str] = None
) -> None:
    '''
    Plots the per-source weighted average density, colored by isotope and
    optionally faceted by a source-level metadata column in `group`.

    Parameters
    ----------
    output_dir : str
        The root directory of the visualization loaded into the browser.
    qsip_data : RS4
        The "qsip_data" object.
    group : str | None
        An optional source-level metadata column used to facet the plot of
        weighted average densities.
    '''
    if group:
        plot = qsip2.plot_source_wads(qsip_data, group=group)
    else:
        plot = qsip2.plot_source_wads(qsip_data)

    _ggplot2_object_to_visualization(
        plot, Path(output_dir), width=10, height=4
    )


def plot_sample_curves(output_dir: str, qsip_data: RS4) -> None:
    '''
    Plots gradient position by relative amount of DNA, faceted by source.

    Parameters
    ----------
    output_dir : str
        The root directory of the visualization loaded into the browser.
    qsip_data : RS4
        The "qsip_data" object.
    '''
    plot = qsip2.plot_sample_curves(qsip_data)

    _ggplot2_object_to_visualization(
        plot, Path(output_dir), width=10, height=10
    )


def plot_density_outliers(output_dir: str, qsip_data: RS4) -> None:
    '''
    Plots gradient position by density, faceted by source, and performs
    Cook's outlier detection.

    Parameters
    ----------
    output_dir : str
        The root directory of the visualization loaded into the browser.
    qsip_data : RS4
        The "qsip_data" object.
    '''
    plot = qsip2.plot_density_outliers(qsip_data)

    _ggplot2_object_to_visualization(
        plot, Path(output_dir), width=10, height=10
    )


def show_comparison_groups(
    output_dir: str, qsip_data: RS4, groups: list
) -> None:
    '''
    Displays a table of ids grouped in columns by isotope, and in rows by the
    given groups.

    Parameters
    ----------
    output_dir : str
        The root directory of the visualization loaded into the browser.
    qsip_data : RS4
        The "qsip_data" object.
    groups : list[str]
        The names of one or more source-level metadata columns used to further
        subdivide the labeled and unlabeled samples.
    '''
    groups_vector = ro.vectors.StrVector(groups)

    with (ro.default_converter + pandas2ri.converter).context():
        df = qsip2.show_comparison_groups(qsip_data, groups_vector)

    df.to_html(Path(output_dir) / 'index.html')
