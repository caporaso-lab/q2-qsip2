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
from rpy2.robjects.methods import RS4
from rpy2.robjects import pandas2ri

import rachis

from q2_qsip2.metadata import standardize_metadata, _extract_source_metadata

qsip2 = importr('qSIP2')
importr('S7')


def standard_workflow(
    table: biom.Table,
    qsip_metadata: rachis.Metadata,
) -> biom.Table:

    return table


def _create_qsip_data(table: biom.Table, metadata: rachis.Metadata) -> RS4:
    '''
    Create a `qsip_data` R object from a feature table and standardized
    metadata.

    Parameters
    ----------
    table : biom.Table
        The feature table containing sample ids on one axis and feature ids
        on the other.
    metadata : rachis.Metadata
        The standardized sample-level metadata containing all required
        sample-level and source-level variables.

    Returns
    -------
    RObject
        The qSIP data object as created by the qSIP2 R package. This wraps the
        sample metadata, the source metadata, and the feature table.
    '''
    # validate metadata by restandardizing
    sample_metadata = standardize_metadata(sample_metadata=metadata)

    # split standardized metadata into sample- & source-level
    source_metadata = _extract_source_metadata(metadata)

    # convert to dataframes
    sample_df = sample_metadata.to_dataframe()
    sample_index_name = sample_df.index.name
    sample_df.reset_index(inplace=True)

    source_df = source_metadata.to_dataframe()
    source_index_name = source_df.index.name
    source_df.reset_index(inplace=True)

    table_df = table.to_dataframe(dense=True)
    table_df.index.name = 'ASV'
    table_df.reset_index(inplace=True)

    # construct qsip object
    with (ro.default_converter + pandas2ri.converter).context():
        R_source_obj = qsip2.qsip_source_data(
            source_df, source_mat_id=source_index_name
        )
        R_sample_obj = qsip2.qsip_sample_data(
            sample_df, sample_id=sample_index_name,
        )
        R_feature_obj = qsip2.qsip_feature_data(
           table_df, feature_id='ASV'
        )
        R_qsip_obj = qsip2.qsip_data(
            source_data=R_source_obj,
            sample_data=R_sample_obj,
            feature_data=R_feature_obj
        )

    return R_qsip_obj


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
    min_unlabeled_sources: int = 1,
    min_labeled_sources: int = 1,
    min_unlabeled_fractions: int = 1,
    min_labeled_fractions: int = 1
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

    source_metadata = _extract_source_metadata(metadata).to_dataframe()

    unlabeled_sources = source_metadata.loc[
        source_metadata['isotope'] == unlabeled_isotope
    ].index
    labeled_sources = source_metadata.loc[
        source_metadata['isotope'] == labeled_isotope
    ].index

    unlabeled_sources_vector = ro.vectors.StrVector(list(unlabeled_sources))
    labeled_sources_vector = ro.vectors.StrVector(list(labeled_sources))

    R_filtered_qsip_obj = qsip2.run_feature_filter(
        R_qsip_obj,
        unlabeled_source_mat_ids=unlabeled_sources_vector,
        labeled_source_mat_ids=labeled_sources_vector,
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


def resample_and_calculate_EAF(
    filtered_qsip_data: RS4,
    resamples: int = 1000,
    random_seed: int = 1,
) -> RS4:
    '''
    Reseample and calculate excess atom fraction (EAF) for each feature.

    Parameters
    ----------
    filtered_qsip_data : RS4
        The filtered "qsip_data" object.
    resamples : int
        The number of bootstrap resamplings to perform.
    random_seed : int
        The random seed to use during resampling. Exposed for reproducibility.
    '''
    resampled_qsip_data = qsip2.run_resampling(
        filtered_qsip_data,
        resamples=resamples,
        with_seed=random_seed
    )

    eaf_qsip_data = qsip2.run_EAF_calculations(resampled_qsip_data)

    return eaf_qsip_data
