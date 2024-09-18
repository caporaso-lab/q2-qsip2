# ----------------------------------------------------------------------------
# Copyright (c) 2024, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import biom
import rpy2.robjects as ro
from rpy2.robjects.packages import importr
from rpy2.robjects.methods import RS4
from rpy2.robjects import pandas2ri

from typing import Optional

import qiime2

from q2_qsip2._wrangling import (
    _construct_column_mapping,
    _handle_metadata,
)

qsip2 = importr('qSIP2')
importr('S7')


def standard_workflow(
    table: biom.Table,
    qsip_metadata: qiime2.Metadata,
) -> biom.Table:

    return table


def create_qsip_data(
    table: biom.Table,
    sample_metadata: qiime2.Metadata,
    source_metadata: Optional[qiime2.Metadata] = None,
    source_mat_id_column: str = 'source_mat_id',
    isotope_column: str = 'isotope',
    isotopolog_column: str = 'isotopolog',
    gradient_position_column: str = 'gradient_position',
    gradient_pos_density_column: str = 'gradient_pos_density',
    gradient_pos_amt_column: str = 'gradient_pos_amt',
) -> RS4:
    '''
    Validates and combines the sample-level and source-level metadata files.
    If no source-level metadata file is provided it is first extracted from the
    sample-level metadata.

    Parameters
    ----------
    table : biom.Table
        The feature table containing sample ids on one axis and feature ids
        on the other.
    sample_metadata : qiime2.Metadata
        The sample-level metadata file.
    source_metadata : qiime2.Metadata
        The source-level metadata file.
    source_mat_id_column : str
        The name of the source material id column in the sample-level metadata.
    isotope_column : str
        The name of the isotope column in the source-level metadata.
    isotopolog_column : str
        The name of the isotopolog column in the source-level metadata.
    gradient_position_column : str
        The name of the gradient position column in the sample-level metadata.
    gradient_pos_density_column : str
        The name of the gradient position density column in the sample-level
        metadata.
    gradient_pos_amt_column : str
        The name of the gradient position amount column in the sample-level
        metadata.

    Returns
    -------
    RObject
        The qSIP data object as created by the qSIP2 R package. This wraps the
        sample metadata, the source metadata, and the feature table.
    '''

    # generate source-level metadata if necessary, and validate both it and
    # sample-level metadata
    column_mapping = _construct_column_mapping(locals())

    source_metadata, sample_metadata = _handle_metadata(
        sample_metadata,
        source_metadata,
        source_mat_id_column,
        column_mapping
    )

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


def subset_and_filter(
    qsip_data: RS4,
    unlabeled_sources: list[str],
    labeled_sources: list[str],
    min_unlabeled_sources: int = 1,
    min_labeled_sources: int = 1,
    min_unlabeled_fractions: int = 1,
    min_labeled_fractions: int = 1
) -> RS4:
    '''
    Subsets the qsip data object to include only those sources listed in
    `unlabeled_sources` and `labeled_sources`, and to include only those
    features that pass the minimum prevalence parameters.

    Parameters
    ----------
    qsip_data : RS4
        The "qsip_data" object.
    unlabeled_sources : list[str]
        The IDs of the unlabeled sources to retain.
    labeled_sources : list[str]
        The IDs of the labeled sources to retain.
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
    '''
    unlabeled_sources_vector = ro.vectors.StrVector(unlabeled_sources)
    labeled_sources_vector = ro.vectors.StrVector(labeled_sources)

    filtered_qsip_data = qsip2.run_feature_filter(
        qsip_data,
        unlabeled_source_mat_ids=unlabeled_sources_vector,
        labeled_source_mat_ids=labeled_sources_vector,
        min_unlabeled_sources=min_unlabeled_sources,
        min_labeled_sources=min_labeled_sources,
        min_unlabeled_fractions=min_unlabeled_fractions,
        min_labeled_fractions=min_labeled_fractions
    )

    return filtered_qsip_data


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
