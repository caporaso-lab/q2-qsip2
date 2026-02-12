# ----------------------------------------------------------------------------
# Copyright (c) 2024, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import altair as alt
import pandas as pd
import rpy2.robjects as ro
from rpy2.robjects.methods import RS4
from rpy2.robjects.packages import importr
from rpy2.robjects import pandas2ri

import importlib
import pathlib
from pathlib import Path
import shutil

import rachis

from q2_qsip2.visualizers._helpers import _ggplot2_object_to_visualization
from q2_qsip2.metadata import _extract_source_metadata

qsip2 = importr('qSIP2')


def plot_weighted_average_densities(
    output_dir: str,
    wads: pd.DataFrame,
    metadata: rachis.Metadata,
    group: str | None = None
):
    '''
    Plot per-source weighted average density values in a strip chart,
    optionally faceted by a `group` variable.

    Parameters
    ----------
    output_dir : str
        The visualization directory.
    wads : pd.DataFrame
        The per-source WADs.
    metadata : rachis.Metadata
        The standardized metadata.
    group : str | None
        An optional source-level variable used to facet the figure.

    Raises
    ------
    ValueError
        If a `group` is given but not found in the source-level metadata.
    '''
    source_metadata_df = _extract_source_metadata(metadata).to_dataframe()
    wads = pd.merge(
        wads,
        source_metadata_df,
        left_on='source_mat_id',
        right_index=True,
        how='inner'
    )

    if group is not None and group not in wads.columns:
        msg = (
            f'Could not find the {group} variable in the source-level metadata.'
        )
        raise ValueError(msg)

    chart = alt.Chart(
        wads, width=100, height=400
    ).mark_circle(size=100).encode(
        x=alt.X(
            'jitter:Q',
            title=None,
            axis=alt.Axis(ticks=False, labels=False, grid=False),
            scale=alt.Scale(padding=10)
        ),
        y=alt.Y(
            'WAD:Q',
            scale=alt.Scale(
                domain=[wads['WAD'].min(), wads['WAD'].max()],
                padding=10
            ),
        ),
        color=alt.Color('isotope:N'),
        tooltip='source_mat_id:N'
    ).transform_calculate(
        jitter='sqrt(-2*log(random()))*cos(2*PI*random())'
    )

    if group:
        chart = chart.encode(
            column=f'{group}:N'
        )

    chart.save(pathlib.Path(output_dir) / 'index.html')


"""
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
"""


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


def plot_filtered_features(output_dir: str, filtered_qsip_data: RS4) -> None:
    '''
    Displays per-source stacked bar charts showing the retention of features.

    Parameters
    ----------
    output_dir : str
        The root directory of the visualization loaded into the browser.
    qsip_data : RS4
        The "qsip_data" object.
    '''
    plot = qsip2.plot_filter_results(filtered_qsip_data)

    _ggplot2_object_to_visualization(
        plot, Path(output_dir), width=10, height=10
    )


def plot_excess_atom_fractions(
    output_dir: str,
    eaf_qsip_data: RS4,
    num_top: int = 50,
    confidence_interval: float = 0.9
) -> None:
    '''
    Plots per-taxon excess atom fraction values.

    Parameters
    ----------
    output_dir : str
        The root directory of the visualization loaded into the browser.
    qsip_data : RS4
        The "qsip_data" object.
    num_top : int
        The number of taxa displayed taken in order of decreasing excess
        atom fraction.
    confidence_interval : float
        The confidence interval to display from the bootstrapped excess atom
        fraction values.
    '''
    plot = qsip2.plot_EAF_values(
        eaf_qsip_data, top=num_top, confidence=confidence_interval, error='bar'
    )

    _ggplot2_object_to_visualization(
        plot, Path(output_dir), width=10, height=10
    )
