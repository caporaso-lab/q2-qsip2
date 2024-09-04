import biom
import pandas as pd
import rpy2
import rpy2.robjects as ro
from rpy2.robjects.packages import importr
from rpy2.robjects import pandas2ri

from typing import Optional

import qiime2

from q2_qsip2._wrangling import (
    _construct_column_mapping,
    _handle_metadata,
    _combine_metadatas,
    _extract_source_metadata
)

importr('qSIP2')


def standard_workflow(
    table: biom.Table,
    qsip_metadata: qiime2.Metadata,
) -> biom.Table:

    # extract source-level metadata
    source_metadata = _extract_source_metadata(
        qsip_metadata, source_column='source_mat_id'
    )

    sample_metadata = qsip_metadata

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

    # construct R objects
    R_qsip_source_data_func = ro.r['qsip_source_data']
    R_qsip_sample_data_func = ro.r['qsip_sample_data']
    R_qsip_feature_data_func = ro.r['qsip_feature_data']

    with (ro.default_converter + pandas2ri.converter).context():
        R_source_obj = R_qsip_source_data_func(
            source_df, source_mat_id=source_index_name
        )

        R_sample_obj = R_qsip_sample_data_func(
            sample_df, sample_id=sample_index_name,
        )

        R_feature_obj = R_qsip_feature_data_func(
           table_df, feature_id='ASV'
        )

    print('source obj is', R_source_obj)
    print('sample obj is', R_sample_obj)
    print('feature obj is', R_feature_obj)

    return table


def generate_qsip_metadata(
    sample_metadata: qiime2.Metadata,
    source_metadata: Optional[qiime2.Metadata] = None,
    source_mat_id_column: str = 'source_mat_id',
    isotope_column: str = 'isotope',
    isotopolog_column: str = 'isotopolog',
    gradient_position_column: str = 'gradient_position',
    gradient_pos_density_column: str = 'gradient_pos_density',
    gradient_pos_amt_column: str = 'gradient_pos_amt',
) -> qiime2.Metadata:
    '''
    Validates and combines the sample-level and source-level metadata files.
    If no source-level metadata file is provided it is first extracted from the
    sample-level metadata. The returned metadata file will have all columns
    required by qSIP2 renamed to their defaults.

    Parameters
    ----------
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
    qiime2.Metadata
        The validated and combined sample- and source-level metadata with the
        columns renamed to their defaults.
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

    # combine the validated metadatas
    return _combine_metadatas(sample_metadata, source_metadata)
