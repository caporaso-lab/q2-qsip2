# ----------------------------------------------------------------------------
# Copyright (c) 2024, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import altair as alt
import biom
import pandas as pd
import rpy2.robjects as ro
from rpy2.robjects.packages import importr
from rpy2.robjects import pandas2ri

import pathlib

import rachis

from q2_qsip2.metadata import _extract_source_metadata
from q2_qsip2._constructors import _create_qsip_data

qsip2 = importr('qSIP2')


def plot_weighted_average_densities(
    output_dir: str,
    source_wads: pd.DataFrame,
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
    source_wads : pd.DataFrame
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
        source_wads,
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
        source_wads, width=100, height=400
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


def plot_sample_curves(
    output_dir: str,
    table: biom.Table,
    metadata: rachis.Metadata,
) -> None:
    '''
    Plots distributions of normalized relative abundances within each source.

    Parameters
    ----------
    output_dir : str
        The visualization directory.
    table : biom.Table
        The feature table.
    metadata : rachis.Metadata
        The standardized metadata.
    '''
    R_qsip_obj = _create_qsip_data(table, metadata)
    with (ro.default_converter + pandas2ri.converter).context():
        norm_rel_abun_df = R_qsip_obj.slots['tube_rel_abundance']

    # sum qPCR-normalized abundances within each sample
    per_sample_rel_abun_df = norm_rel_abun_df.groupby(
        'sample_id', as_index=False
    ).agg({
        'tube_rel_abundance': 'sum',
    })

    per_sample_rel_abun_df = pd.merge(
        per_sample_rel_abun_df,
        metadata.to_dataframe(),
        left_on='sample_id',
        right_index=True,
        how='inner'
    )

    base = alt.Chart(per_sample_rel_abun_df).encode(
        x=alt.X('gradient_pos_density:Q'),
        y=alt.Y('tube_rel_abundance:Q'),
        color='source_mat_id:N',
    )

    line = base.mark_line(interpolate='cardinal').encode(
        strokeDash='isotope:N'
    )
    point = base.mark_circle(size=50).encode(tooltip=[
        'sample_id:N', 'gradient_pos_density:Q', 'tube_rel_abundance:Q'
    ])
    chart = line + point

    chart = chart.facet(
        facet='source_mat_id:N', columns=5
    ).resolve_scale(
        x='independent',
        y='independent'
    )

    chart.save(pathlib.Path(output_dir) / 'index.html')


def plot_density_outliers(output_dir: str, metadata: rachis.Metadata) -> None:
    '''
    Plots gradient position (fraction) by gradient position density to show
    any trend outliers.

    Parameters
    ----------
    output_dir : str
        The visualization directory.
    metadata : rachis.Metadata
        The standardized metadata.
    '''
    metadata_df = metadata.to_dataframe().reset_index(names='sample_id')

    base = alt.Chart(metadata_df).encode(
        x=alt.X('gradient_position:Q'),
        y=alt.Y(
            'gradient_pos_density:Q',
            scale=alt.Scale(zero=False)
        ),
    )

    point = base.mark_circle(size=50).encode(
        tooltip=['sample_id:N', 'gradient_position:Q', 'gradient_pos_density:N']
    )

    regression = base.transform_regression(
        'gradient_position', 'gradient_pos_density',
        groupby=['source_mat_id']
    ).mark_line(color='orange')

    chart = alt.layer(regression, point).facet(
        facet='source_mat_id:N',
        columns=5,
    ).resolve_scale(
        x='independent',
        y='independent'
    )

    chart.save(pathlib.Path(output_dir) / 'index.html')


def plot_excess_atom_fractions(
    output_dir: str,
    excess_atom_fractions: pd.DataFrame,
    num_top: int = 50,
    confidence_interval: float = 0.9
) -> None:
    '''
    Plots per-taxon excess atom fraction values.

    Parameters
    ----------
    output_dir : str
        The root directory of the visualization loaded into the browser.
    excess_atom_fractions : pd.DataFrame
        The per-feature excess atom fraction bootstrap samples.
    num_top : int
        The number of taxa displayed taken in order of decreasing excess
        atom fraction.
    confidence_interval : float
        The confidence interval to display from the bootstrapped excess atom
        fraction values.
    '''
    alpha = (1 - confidence_interval) / 2

    resampled_df = excess_atom_fractions[~excess_atom_fractions['observed']]
    observed_df = excess_atom_fractions[excess_atom_fractions['observed']]

    summarized_df = resampled_df.groupby(
        'feature_id', as_index=False
    ).agg(
        mean_EAF=('EAF', 'mean'),
        lower=('EAF', lambda s: s.quantile(alpha)),
        upper=('EAF', lambda s: s.quantile(1 - alpha)),
    )

    all_eaf_df = pd.merge(
        observed_df, summarized_df, on='feature_id', how='left'
    )

    all_eaf_df.sort_values(by='EAF', inplace=True, ascending=False)
    all_eaf_df = all_eaf_df.iloc[0: min(num_top, len(all_eaf_df)), :]

    points = alt.Chart(all_eaf_df).mark_circle(size=80).encode(
        x=alt.X('EAF:Q'),
        y=alt.Y(
            'feature_id:N', sort=alt.SortField(field='EAF', order='descending')
        ),
        tooltip=['feature_id:N', 'EAF:Q'],
    )

    x_axis_title = (
        f'Excess Atom Fraction, {confidence_interval} confidence interval'
    )
    intervals = alt.Chart(all_eaf_df).mark_errorbar().encode(
        x=alt.X('lower:Q', title=x_axis_title),
        x2='upper:Q',
        y=alt.Y(
            'feature_id:N', sort=alt.SortField(field='EAF', order='descending')
        ),
        tooltip=alt.value(None)
    )

    chart = intervals + points

    chart.save(pathlib.Path(output_dir) / 'index.html')
