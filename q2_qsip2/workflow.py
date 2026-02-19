# ----------------------------------------------------------------------------
# Copyright (c) 2024, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import biom
import pandas as pd
import rpy2.robjects as ro
from rpy2.robjects.packages import importr
from rpy2.robjects import pandas2ri

import rachis

from q2_qsip2.metadata import _get_source_vectors
from q2_qsip2._constructors import (
    _create_qsip_data, _create_filtered_qsip_data,
)

qsip2 = importr('qSIP2')
base = importr('base')
importr('S7')


def calculate_weighted_average_densities(
    table: biom.Table, metadata: rachis.Metadata
) -> pd.DataFrame:
    '''
    Calculate per-source weighted average densities (WADs).

    Parameters
    ----------
    table : biom.Table
        The feature table.
    metadata : rachis.Metadata
        The standardized metadata.

    Returns
    -------
    pd.DataFrame
        The per-source WADs.
    '''
    R_qsip_obj = _create_qsip_data(table, metadata)

    with (ro.default_converter + pandas2ri.converter).context():
        return qsip2.source_wads(R_qsip_obj)


def filter_by_prevalence(
    table: biom.Table,
    metadata: rachis.Metadata,
    unlabeled_isotope: str = '16O',
    labeled_isotope: str = '18O',
    min_unlabeled_sources: int = 2,
    min_labeled_sources: int = 2,
    min_unlabeled_fractions: int = 2,
    min_labeled_fractions: int = 2
) -> (pd.DataFrame, pd.DataFrame):
    '''
    Filters `table` to include only those features that pass the minimum
    prevalence parameters.

    Parameters
    ----------
    table : biom.Table
        The feature table.
    metadata : rachis.Metadata
        The standardized qSIP2 metadata.
    unlabeled_isotope : str
        The metadata value corresponding to the unlabeled isotope.
    labeled_isotope : str
        The metadata value corresponding to the labeled isotope.
    min_unlabeled_sources : int
        The minimum number of unlabeled sources a feature must be present in
        to be retained.
    min_labeled_sources : int
        The minimum number of labeled sources a feature must be present in
        to be retained.
    min_unlabeled_fractions : int
        The minimum number of fractions a feature must be present in
        to be considered present in an unlabeled source.
    min_labeled_fractions : int
        The minimum number of fractions a feature must be present in
        to be considered present in a labeled source.

    Returns
    -------
    tuple[pd.DataFrame]
        The filtered feature table and the filtered source weighted average
        densities.
    '''
    R_qsip_obj = _create_qsip_data(table, metadata)

    unlabeled_sources, labeled_sources = _get_source_vectors(
        table, metadata, unlabeled_isotope, labeled_isotope
    )

    R_filtered_qsip_obj = qsip2.run_feature_filter(
        R_qsip_obj,
        unlabeled_source_mat_ids=unlabeled_sources,
        labeled_source_mat_ids=labeled_sources,
        min_unlabeled_sources=min_unlabeled_sources,
        min_labeled_sources=min_labeled_sources,
        min_unlabeled_fractions=min_unlabeled_fractions,
        min_labeled_fractions=min_labeled_fractions
    )

    with (ro.default_converter + pandas2ri.converter).context():
        filtered_table_df = R_filtered_qsip_obj.slots['filtered_feature_data']
        filtered_source_wads_df = R_filtered_qsip_obj.slots[
            'filtered_wad_data'
        ]

    filtered_table_df = filtered_table_df.set_index('feature_id').T
    filtered_table_df.index.name = 'sample-id'

    return filtered_table_df, filtered_source_wads_df


def calculate_excess_atom_fractions(
    table: biom.Table,
    feature_wads: pd.DataFrame,
    metadata: rachis.Metadata,
    unlabeled_isotope: str = '16O',
    labeled_isotope: str = '18O',
    resamples: int = 1000,
    random_seed: int = 1,
    allow_resampling_failures: bool = False,
) -> pd.DataFrame:
    '''
    Reseample and calculate excess atom fraction (EAF) for each feature.

    Parameters
    ----------
    table : biom.Table
        The feature table.
    feature_wads : pd.DataFrame
        The per-feature weighted average densities.
    metadata : rachis.Metadata
        The standardized qSIP2 metadata.
    unlabeled_isotope : str
        The metadata value corresponding to the unlabeled isotope.
    labeled_isotope : str
        The metadata value corresponding to the labeled isotope.
    resamples : int
        The number of bootstrap resamplings to perform.
    random_seed : int
        The random seed to use during resampling. Exposed for reproducibility.
    allow_resampling_failures : bool
        Whether to allow bootstrapped per-feature weighted average density
        vectors that contain all-NA values. Allow means discard such samples,
        disallow means throw an error.
    '''
    R_filtered_qsip_data = _create_filtered_qsip_data(
        table, feature_wads, metadata, unlabeled_isotope, labeled_isotope
    )

    R_resampled_qsip_data = qsip2.run_resampling(
        R_filtered_qsip_data,
        resamples=resamples,
        with_seed=random_seed,
        allow_failures=allow_resampling_failures,
    )

    eaf_qsip_data = qsip2.run_EAF_calculations(R_resampled_qsip_data)

    with (ro.default_converter + pandas2ri.converter).context():
        return eaf_qsip_data.slots['EAF']
