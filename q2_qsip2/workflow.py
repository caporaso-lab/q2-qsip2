import biom
import pandas as pd
import rpy2
import rpy2.robjects as ro
from rpy2.robjects.packages import importr

from typing import Optional

import qiime2

from q2_qsip2._wrangling import (
    _construct_column_mapping,
    _handle_metadata,
    SOURCE_COLUMNS,
    SAMPLE_COLUMNS
)

importr('qSIP2')


def standard_workflow(
    table: biom.Table,
    sample_metadata: qiime2.Metadata,
    source_metadata: qiime2.Metadata = None,
    split_metadata: bool = False,
    source_mat_id_column: str = 'source_mat_id',
    isotope_column: str = 'isotope',
    isotopolog_column: str = 'isotopolog',
    gradient_position_column: str = 'gradient_position',
    gradient_position_density_column: str = 'gradient_pos_density',
    gradient_position_amount_column: str = 'gradient_pos_amt',
) -> biom.Table:
    # generate source-level metadata if necessary, and validate both it and
    # sample-level metadata
    column_mapping = _construct_column_mapping(locals())
    source_df, sample_df = _handle_metadata(
        sample_metadata, source_metadata, source_mat_id_column, column_mapping
    )

    # get identifier column names of both metadatas
    if source_metadata is not None:
        source_id = source_metadata.to_dataframe().index.name
    else:
        # hardcoded in `q2_qsip2._extract_source_metadata`
        source_id = 'id'

    sample_id = sample_metadata.to_dataframe().index.name

    table_df = table.to_dataframe()

    # construct R objects
    R_qsip_source_data_func = ro.r['qsip_source_data']
    R_source_obj = R_qsip_source_data_func(source_df, source_mat_id=source_id)

    R_qsip_sample_data_func = ro.r['qsip_sample_data']
    R_sample_obj = R_qsip_sample_data_func(
        sample_df, sample_id = sample_id, source_mat_id=source_mat_id_column
    )

    print('source obj is, ', R_source_obj)
    print('sample obj is, ', R_sample_obj)

    return table
