# ----------------------------------------------------------------------------
# Copyright (c) 2024, Colin Wood.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import pandas as pd

import qiime2


SOURCE_COLUMNS = (
    'isotope',
    'isotopolog',
    'source_mat_id',
)


SAMPLE_COLUMNS = (
    'sample_id',
    'souce_mat_id',
    'gradient_position',
    'gradient_pos_density',
    'gradient_pos_amt',
)


def _extract_source_metadata(
    source_md: qiime2.Metadata,
    source_column: str,
) -> pd.DataFrame:
    '''
    Extract source-level metadata from sample-level metadata. The input
    source-level metadata must have a column that indicates which source each
    sample belongs to.

    The columns that are selected as source-level are those that after grouping
    on `source_column` only have one unique value in each group. That is, those
    that vary no more than `source_column`. These are likely to be source-level
    metadata columns.

    Parameters
    ----------
    source_md : qiime2.Metadata
        The source-level metadata (row per sequenced fraction).
    source_column : str
        The column name of the source identifier for each sample. The unique
        values of this determine the rows of the returned metadata.

    Returns
    -------
    The extracted source-level metadata.
    '''
    source_df = source_md.to_dataframe().reset_index()

    grouped_df = source_df.groupby(source_column, as_index=False)
    unique_counts = grouped_df.nunique()
    source_level_cols = unique_counts.columns[
        (unique_counts == 1).all() | (unique_counts.columns == source_column)
    ]
    sample_df = grouped_df.head(1)[source_level_cols]

    return sample_df


def _validate_metadata_columns(
    metadata: qiime2.Metadata, columns_mapping: dict, metadata_type: str
) -> None:
    '''
    Asserts that all columns specified in `columns_mapping` are in
    `metadata`.

    Parameters
    ----------
    metadata : qiime2.Metadata
        The metadata to validate.
    columns_mapping : dict[str, str]
        A column mapping from default name to provided name, for each pairing
        of which either the default or the provided name ought to exist in
        `metadata`.
    metadata_type : str
        One of "source", "sample".

    Returns
    -------
    None
        Silence do be kinda gold doe.

    Raises
    ------
    ValueError
        If one or more of `columns` are not present in `metadata`.
    '''
    md_df = metadata.to_dataframe().reset_index()

    columns = []
    for default, provided in columns_mapping.items():
        if provided is None:
            columns.append(default)
        else:
            columns.append(provided)

    shared_columns = md_df.columns.intersection(columns)
    if len(shared_columns) != len(columns):
        error_string = (
            'The following required columns were not found in the '
            f'{metadata_type} metadata:\n\n'
            f'{"Default":^25} | {"Provided":^25}\n'
            f'{"-" * 23:^25} | {"-" * 23:^25}'
        )

        inverted_columns_mapping = {}
        for default, provided in columns_mapping.items():
            if provided is not None:
                inverted_columns_mapping[provided] = default

        missing = set(columns) - set(shared_columns)
        for column in missing:
            if column in columns_mapping:
                default = column
                provided = 'N/A (default used)'
            else:
                default = inverted_columns_mapping[column]
                provided = column

            error_string += f'\n{default:^25} | {provided:^25}'

        error_string += (
            '\n\nPlease update the column names passed to the method '
            'or update your metadata to use the defaults.'
        )

        raise ValueError(error_string)
