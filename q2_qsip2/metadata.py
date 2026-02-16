# ----------------------------------------------------------------------------
# Copyright (c) 2024, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import warnings

import pandas as pd

import rachis
from rachis.core.exceptions import RachisWarning


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
    sample_md: rachis.Metadata,
    source_column: str = 'source_mat_id',
) -> rachis.Metadata:
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
    sample_md : rachis.Metadata
        The sample-level metadata (row per sequenced fraction).
    source_column : str
        The column name of the source identifier for each sample. The unique
        values of this determine the rows of the returned metadata.

    Returns
    -------
    rachis.Metadata
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

    # must rename to 'id' so that `rachis.Metadata` is happy
    source_df.rename({source_column: 'id'}, axis=1, inplace=True)
    source_df.set_index('id', inplace=True)

    return rachis.Metadata(source_df)


def _merge_metadatas(
    source_metadata: rachis.Metadata,
    sample_metadata: rachis.Metadata,
) -> rachis.Metadata:
    '''
    Merges source- and sample-level metadata into a single sample-level
    metadata object. The merged metadata object will have all source-level
    variable values simply repeated for each sample within each source. Any
    variables present in both the source- and sample-level metadata are
    discarded from the source-level metadata before merging.

    Note: it's assumed that `sample_metadata` and `source_metadata` have all
    the expected default column namings.

    Parameters
    ----------
    source_metadata : rachis.Metadata
        The source-level metadata.
    sample_metadata : rachis.Metadata
        The sample-level metadata.

    Returns
    -------
    rachis.Metadata
        The merged sample-level metadata.
    '''
    sample_md_df = sample_metadata.to_dataframe().reset_index(
        names='original_sample_identifier'
    )
    source_md_df = source_metadata.to_dataframe().reset_index(
        names='original_source_identifier'
    )

    _validate_source_id_overlap(
        set(sample_md_df['source_mat_id']),
        set(source_md_df['original_source_identifier'])
    )

    for column in set(sample_md_df.columns) & set(source_md_df.columns):
        source_md_df.drop(column, axis=1, inplace=True)

    merged_df = pd.merge(
        sample_md_df,
        source_md_df,
        left_on='source_mat_id',
        right_on='original_source_identifier',
        how='inner'
    )

    merged_df.drop('original_source_identifier', axis=1, inplace=True)
    merged_df.set_index('original_sample_identifier', inplace=True)
    merged_df.index.name = 'id'

    return rachis.Metadata(merged_df)


def _validate_source_id_overlap(
    sample_level_source_ids: set, source_level_source_ids: set
) -> None:
    '''
    Ensure that at least some source IDs overlap between the sample-level and
    source-level metadata. Warn if the two sets are not equivalent.

    Parameters
    ----------
    sample_level_source_ids : set[str]
        The source IDs present in the sample-level metadata.
    source_level_source_ids : set[str]
        The source IDs present in the source-level metadata.

    Raises
    ------
    ValueError
        If no IDs are shared.

    Warns
    _____
    RachisWarning
        If the two sets of IDs are not equal.
    '''
    if (sample_level_source_ids & source_level_source_ids) == set():
        msg = (
            'There were no shared source IDs between the sample-level '
            'and source-level metadata files.'
        )
        raise ValueError(msg)

    if sample_level_source_ids != source_level_source_ids:
        sample_only_ids = sample_level_source_ids - source_level_source_ids
        source_only_ids = source_level_source_ids - sample_level_source_ids
        msg = (
            'There was a misalignment between the source IDs in the '
            'sample-level metadata and those in the source-level metadata. '
            'Proceeding with only those source IDs present in both.\n'
        )
        if sample_only_ids:
            msg += (
                'The following source IDs were found only in the sample-level '
                f'metadata: {sample_only_ids}.\n'
            )
        if source_only_ids:
            msg += (
                'The following source IDs were found only in the source-level '
                f'metadata: {source_only_ids}.\n'
            )

        warnings.warn(msg, RachisWarning)


def _validate_and_rename_columns(
    source_metadata: rachis.Metadata,
    sample_metadata: rachis.Metadata,
    source_column: str,
    column_mapping: dict,
) -> tuple[rachis.Metadata, rachis.Metadata]:
    '''
    Validates the input metadata and extracts source-level metadata from
    sample-level metadata if necessary.

    Parameters
    ----------
    source_metadata : rachis.Metadata or None
        The source-level metadata, if provided.
    sample_metadata : rachis.Metadata
        The sample-level metadata.
    source_column : str
        The column name, in the sample metadata, of the source identifier for
        each sample.
    column_mapping : dict[str, str]
        A mapping from default column name to provided name, for each pairing
        of which either the default or the provided name ought to exist in
        the relevant metadata.

    Returns
    -------
    tuple[rachis.Metadata]
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
    metadata: rachis.Metadata,
    column_mapping: dict,
    metadata_type: str,
    extracted: bool = False
) -> rachis.Metadata:
    '''
    Asserts that all columns specified in `columns_mapping` are in
    `metadata`. Then renames all non-default columns to their defaults.

    Parameters
    ----------
    metadata : rachis.Metadata
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
    rachis.Metadata
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

    return rachis.Metadata(md_df)


def standardize_metadata(
    sample_metadata: rachis.Metadata,
    source_metadata: rachis.Metadata | None = None,
    source_mat_id_column: str = 'source_mat_id',
    isotope_column: str = 'isotope',
    isotopolog_column: str = 'isotopolog',
    gradient_position_column: str = 'gradient_position',
    gradient_pos_density_column: str = 'gradient_pos_density',
    gradient_pos_amt_column: str = 'gradient_pos_amt',
) -> rachis.Metadata:
    '''
    Parameters
    ----------
    sample_metadata : rachis.Metadata
        The sample-level metadata file.
    source_metadata : rachis.Metadata | None
        The optional source-level metadata file.
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
    ImmutabaleMetadata
        The standardized sample-level qSIP metadata.
    '''
    column_mapping = _construct_column_mapping(locals())

    source_metadata, sample_metadata = _validate_and_rename_columns(
        source_metadata,
        sample_metadata,
        source_mat_id_column,
        column_mapping,
    )

    merged_metadata = _merge_metadatas(source_metadata, sample_metadata)

    return merged_metadata
