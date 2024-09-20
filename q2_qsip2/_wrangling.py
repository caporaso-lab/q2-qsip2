# ----------------------------------------------------------------------------
# Copyright (c) 2024, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from typing import Optional

import qiime2


SOURCE_COLUMNS = (
    'isotope',
    'isotopolog',
)


SAMPLE_COLUMNS = (
    'gradient_position',
    'gradient_pos_density',
    'gradient_pos_amt',
    'source_mat_id',
)


ALL_COLUMNS = SOURCE_COLUMNS + SAMPLE_COLUMNS


def _construct_column_mapping(arguments: dict) -> dict:
    '''
    Construct a mapping from default column name to provided name from
    `arguments`, which is a `locals()` from another function.

    Parameters
    ----------
    arguments : dict[str, str]
        A `locals()` dictionary that is a superset of the desired column
        mapping.

    Returns
    -------
    dict[str, str]
        A mapping of default column name to provided column name for all
        required qSIP column names across both source- and sample-level
        metadata.
    '''
    column_mapping = {}
    for default, provided in arguments.items():
        default = default.removesuffix('_column')
        if default in ALL_COLUMNS:
            if default == provided:
                column_mapping[default] = None
            else:
                column_mapping[default] = provided

    return column_mapping


def _extract_source_metadata(
    sample_md: qiime2.Metadata,
    source_column: str,
) -> qiime2.Metadata:
    '''
    Extract source-level metadata from sample-level metadata. The input
    source-level metadata must have a column that indicates which source each
    sample belongs to.

    The columns that are selected as source-level are those that after grouping
    on `source_column` only have one unique value in each group. That is, those
    that vary no more than `source_column`. These are likely to be source-level
    metadata columns.

    Note that the `source_column` is renamed to 'id'.

    Parameters
    ----------
    sample_md : qiime2.Metadata
        The sample-level metadata (row per sequenced fraction).
    source_column : str
        The column name of the source identifier for each sample. The unique
        values of this determine the rows of the returned metadata.

    Returns
    -------
    qiime2.Metadata
        The extracted source-level metadata.
    '''
    sample_df = sample_md.to_dataframe().reset_index()

    if source_column not in sample_df.columns:
        error_msg = (
            f'The source material identifier column "{source_column}" was '
            'not found in the sample-level metadata. Please either update '
            'the parameter value or your metadata.'
        )
        raise ValueError(error_msg)

    grouped_df = sample_df.groupby(source_column, as_index=False)
    unique_counts = grouped_df.nunique()
    source_level_cols = unique_counts.columns[
        (unique_counts == 1).all() | (unique_counts.columns == source_column)
    ]
    source_df = grouped_df.head(1)[source_level_cols]

    # must rename to 'id' so that `qiime2.Metadata` is happy
    source_df.rename({source_column: 'id'}, axis=1, inplace=True)
    source_df.set_index('id', inplace=True)

    return qiime2.Metadata(source_df)


def _handle_metadata(
    sample_metadata: qiime2.Metadata,
    source_metadata: Optional[qiime2.Metadata],
    source_column: str,
    column_mapping: dict,
) -> tuple[qiime2.Metadata, qiime2.Metadata]:
    '''
    Validates the input metadata and extracts source-level metadata from
    sample-level metadata if necessary.

    Parameters
    ----------
    sample_metadata : qiime2.Metadata
        The sample-level metadata.
    source_metadata : qiime2.Metadata or None
        The source-level metadata, if provided.
    source_column : str
        The column name, in the sample metadata, of the source identifier for
        each sample.
    column_mapping : dict[str, str]
        A mapping from default column name to provided name, for each pairing
        of which either the default or the provided name ought to exist in
        the relevant metadata.

    Returns
    -------
    tuple[qiime2.Metadata]
        The source and sample metadata tables.
    '''
    # extract source-level metadata if only sample-level metadata was provided
    extracted = False
    if source_metadata is None:
        extracted = True
        source_metadata = _extract_source_metadata(
            sample_metadata, source_column
        )

    # split column mapping into source-, sample-specific mappings
    source_column_mapping = {}
    sample_column_mapping = {}
    for default, provided in column_mapping.items():
        if default in SOURCE_COLUMNS:
            source_column_mapping[default] = provided
        elif default in SAMPLE_COLUMNS:
            sample_column_mapping[default] = provided

    # validate both metadatas
    source_metadata = _validate_metadata_columns(
        source_metadata,
        source_column_mapping,
        metadata_type='source',
        extracted=extracted
    )
    sample_metadata = _validate_metadata_columns(
        sample_metadata,
        sample_column_mapping,
        metadata_type='sample',
    )

    return (source_metadata, sample_metadata)


def _validate_metadata_columns(
    metadata: qiime2.Metadata,
    column_mapping: dict,
    metadata_type: str,
    extracted: bool = False
) -> qiime2.Metadata:
    '''
    Asserts that all columns specified in `columns_mapping` are in
    `metadata`. Then renames all non-default columns to their defaults.

    Parameters
    ----------
    metadata : qiime2.Metadata
        The metadata to validate.
    column_mapping : dict[str, str]
        A mapping from default column name to provided name, for each pairing
        of which either the default or the provided name ought to exist in
        `metadata`.
    metadata_type : str
        One of 'source', 'sample'.
    extracted : bool
        Whether `metadata` was extracted from another metadata. Applies only
        if `metadata_type` is "source". Used only to clarify the error message.

    Returns
    -------
    qiime2.Metadata
        The input `metadata` with the non-default columns renamed to defaults.

    Raises
    ------
    ValueError
        If one or more of the columns in `column_mapping` are not present in
        `metadata`.
    '''
    md_df = metadata.to_dataframe()
    index_name = md_df.index.name
    md_df.reset_index(inplace=True)

    columns = []
    for default, provided in column_mapping.items():
        if provided is None:
            columns.append(default)
        else:
            columns.append(provided)

    shared_columns = md_df.columns.intersection(columns)

    if len(shared_columns) != len(columns):
        error_string = (
            'The following required columns were not found in the '
            f'{"extracted " if extracted else ""}{metadata_type} metadata:\n\n'
            f'{"Default":^25} | {"Provided":^25}\n'
            f'{"-" * 23:^25} | {"-" * 23:^25}'
        )

        inverted_columns_mapping = {}
        for default, provided in column_mapping.items():
            if provided is not None:
                inverted_columns_mapping[provided] = default

        missing = set(columns) - set(shared_columns)
        for column in missing:
            if column in column_mapping:
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

        if metadata_type == 'source':
            error_string += (
                '\n\nIf the column(s) exist in your sample-level metadata, '
                'make sure that its values do not vary within each source.'
            )

        raise ValueError(error_string)

    # otherwise if all columns present, change column names
    rename_columns = {
        provided: default for default, provided in column_mapping.items()
        if provided is not None
    }
    md_df.rename(rename_columns, axis=1, inplace=True)

    md_df.set_index(index_name, inplace=True)

    return qiime2.Metadata(md_df)
