# ----------------------------------------------------------------------------
# Copyright (c) 2024-2026, QIIME 2 development team.
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

from q2_qsip2.metadata import (
    standardize_metadata, _extract_source_metadata, _get_source_vectors
)

qsip2 = importr('qSIP2')
base = importr('base')
importr('S7')


def _create_qsip_data(
    table: biom.Table, metadata: rachis.Metadata, relative: bool = False
) -> RS4:
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
    relative : bool
        Whether `table` is in relative frequency format.

    Returns
    -------
    RObject
        The qSIP2 data object as created by the qSIP2 R package. This wraps the
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
           table_df,
           feature_id='ASV',
           type='relative' if relative else 'counts'
        )
        R_qsip_obj = qsip2.qsip_data(
            source_data=R_source_obj,
            sample_data=R_sample_obj,
            feature_data=R_feature_obj
        )

    return R_qsip_obj


def _create_filtered_qsip_data(
    table: biom.Table,
    feature_wads: pd.DataFrame,
    metadata: rachis.Metadata,
    unlabeled_isotope: str,
    labeled_isotope: str,
) -> RS4:
    '''
    Parameters
    ----------
    table : biom.Table
        The feature table.
    feature_wads : pd.DataFrame
        The per-feature weighted average density values.
    metadata : rachis.Metadata
        The standardized qSIP2 metadata.
    unlabeled_isotope : str
        The metadata value corresponding to the unlabeled isotope.
    labeled_isotope : str
        The metadata value corresponding to the labeled isotope.

    Returns
    -------
    RS4
        A qSIP2 data object with the necessary state to be considered to have
        gone through filtering.
    '''
    R_qsip_object = _create_qsip_data(table, metadata, relative=True)

    R_qsip_object.slots['filtered_feature_data'] = R_qsip_object.slots[
        'feature_data'
    ]

    with (ro.default_converter + pandas2ri.converter).context():
        R_qsip_object.slots['filtered_wad_data'] = feature_wads

    R_feature_wads = R_qsip_object.slots['filtered_wad_data']
    R_feature_wads.rownames = ro.NULL
    R_qsip_object.slots['filtered_wad_data'] = R_feature_wads

    status = R_qsip_object.slots['status']
    status.rx2['filtered'] = True
    R_qsip_object.slots['status'] = status

    unlabeled_sources, labeled_sources = _get_source_vectors(
        table, metadata, unlabeled_isotope, labeled_isotope
    )
    retained_features = ro.vectors.StrVector(
        list(table.ids(axis='observation'))
    )
    R_filter_results = R_qsip_object.slots['filter_results']
    R_filter_results.rx2['unlabeled_source_mat_ids'] = unlabeled_sources
    R_filter_results.rx2['labeled_source_mat_ids'] = labeled_sources
    R_filter_results.rx2['retained_features'] = retained_features
    R_qsip_object.slots['filter_results'] = R_filter_results

    return R_qsip_object
