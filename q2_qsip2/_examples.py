# ----------------------------------------------------------------------------
# Copyright (c) 2024-2026, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import importlib.resources
import pathlib

import rachis


def _get_data_from_tests(subpath: pathlib.Path):
    return importlib.resources.files('q2_qsip2') / 'tests' / 'data' / subpath


def source_md_factory():
    return rachis.Metadata.load(_get_data_from_tests('source.tsv'))


def sample_md_factory():
    return rachis.Metadata.load(_get_data_from_tests('sample.tsv'))


def table_factory():
    return rachis.Artifact.load(_get_data_from_tests('feature-table.qza'))


def tutorial_runthrough(use):
    source_metadata = use.init_metadata('source_metadata', source_md_factory)
    sample_metadata = use.init_metadata('sample_metadata', sample_md_factory)
    table = use.init_artifact('table', table_factory)

    standardized_md, = use.action(
        use.UsageAction('qsip2', 'standardize_metadata'),
        use.UsageInputs(
            sample_metadata=sample_metadata,
            source_metadata=source_metadata,
            source_mat_id_column='source',
            isotope_column='Isotope',
            gradient_position_column='Fraction',
            gradient_pos_density_column='density_g_ml',
            gradient_pos_amt_column='avg_16S_g_soil',
        ),
        use.UsageOutputNames(
            standardized_metadata='standardized_md'
        )
    )
    standardized_md.assert_output_type('ImmutableMetadata')

    metadata = use.view_as_metadata('metadata', standardized_md)

    density_outliers, = use.action(
        use.UsageAction('qsip2', 'plot_density_outliers'),
        use.UsageInputs(metadata=metadata),
        use.UsageOutputNames(visualization='density_outliers')
    )
    density_outliers.assert_output_type('Visualization')

    source_wads, = use.action(
        use.UsageAction('qsip2', 'calculate_source_WADs'),
        use.UsageInputs(
            table=table,
            metadata=metadata,
        ),
        use.UsageOutputNames(source_wads='source_wads')
    )
    source_wads.assert_output_type('SourceData[SourceWAD]')

    source_wads_visualization, = use.action(
        use.UsageAction('qsip2', 'plot_source_WADs'),
        use.UsageInputs(
            source_wads=source_wads,
            metadata=metadata,
        ),
        use.UsageOutputNames(
            visualization='source_wads_visualization'
        )
    )
    source_wads_visualization.assert_output_type('Visualization')

    density_distributions, = use.action(
        use.UsageAction('qsip2', 'plot_density_distributions'),
        use.UsageInputs(
            table=table,
            metadata=metadata,
        ),
        use.UsageOutputNames(
            visualization='density_distributions'
        )
    )
    density_distributions.assert_output_type('Visualization')

    filtered_table, feature_wads = use.action(
        use.UsageAction('qsip2', 'calculate_feature_WADs'),
        use.UsageInputs(
            table=table,
            metadata=metadata,
            unlabeled_isotope='12C',
            labeled_isotope='13C',
            min_unlabeled_sources=1,
            min_labeled_sources=1,
            min_unlabeled_fractions=2,
            min_labeled_fractions=2
        ),
        use.UsageOutputNames(
            filtered_table='filtered_table',
            feature_wads='feature_wads'
        )
    )
    filtered_table.assert_output_type('FeatureTable[RelativeFrequency]')
    feature_wads.assert_output_type('FeatureTable[FeatureWAD]')

    filtering_results, = use.action(
        use.UsageAction('qsip2', 'plot_filtering_results'),
        use.UsageInputs(
            unfiltered_table=table,
            filtered_table=filtered_table,
            metadata=metadata
        ),
        use.UsageOutputNames(
            visualization='filtering_results'
        )
    )
    filtering_results.assert_output_type('Visualization')

    feature_eafs, = use.action(
        use.UsageAction('qsip2', 'calculate_feature_EAFs'),
        use.UsageInputs(
            table=filtered_table,
            feature_wads=feature_wads,
            metadata=metadata,
            unlabeled_isotope='12C',
            labeled_isotope='13C',
            allow_resampling_failures=True
        ),
        use.UsageOutputNames(
            feature_eafs='feature_eafs'
        )
    )
    feature_eafs.assert_output_type('FeatureData[EAF]')

    feature_eafs_visualization, = use.action(
        use.UsageAction('qsip2', 'plot_feature_EAFs'),
        use.UsageInputs(
            feature_eafs=feature_eafs,
            num_top=10
        ),
        use.UsageOutputNames(visualization='feature_eafs_visualizaton')
    )
    feature_eafs_visualization.assert_output_type('Visualization')
