# ----------------------------------------------------------------------------
# Copyright (c) 2024, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import importlib

from qiime2.plugin import (
    Citations, Float, Int, List, Metadata, Plugin, Str, Choices, Bool
)
from q2_types.feature_table import FeatureTable, Frequency, RelativeFrequency
from q2_types.metadata import ImmutableMetadata
from q2_types.sample_data import SampleData
from q2_types.feature_data import FeatureData

from q2_qsip2 import __version__
from q2_qsip2.types import SourceData, SourceWAD, FeatureWAD, EAF
from q2_qsip2.workflow import (
    calculate_weighted_average_densities, filter_by_prevalence,
    calculate_excess_atom_fractions,
)
from q2_qsip2.metadata import standardize_metadata
from q2_qsip2.visualizers._visualizers import (
    plot_weighted_average_densities, plot_sample_curves, plot_density_outliers,
    plot_filtered_features, plot_excess_atom_fractions
)


citations = Citations.load("citations.bib", package="q2_qsip2")

plugin = Plugin(
    name="qsip2",
    version=__version__,
    website="www.qiime2.org",
    package="q2_qsip2",
    description=(
        "A plugin for analyzing quantitative stable isotope probing (qSIP) "
        "data."
    ),
    short_description="Analyze qSIP data.",
    citations=[citations['Caporaso-Bolyen-2024']]
)

plugin.methods.register_function(
    function=standardize_metadata,
    inputs={},
    parameters={
        'sample_metadata': Metadata,
        'source_metadata': Metadata,
        'source_mat_id_column': Str,
        'isotope_column': Str,
        'isotopolog_column': Str,
        'gradient_position_column': Str,
        'gradient_pos_density_column': Str,
        'gradient_pos_amt_column': Str,
    },
    outputs=[
        ('standardized_metadata', ImmutableMetadata)
    ],
    input_descriptions={},
    parameter_descriptions={
        'sample_metadata': 'The sample-level metadata.',
        'source_metadata': 'The source-level metadata.',
        'source_mat_id_column': (
            'The name of the source material id column in the sample-level '
            'metadata.'
        ),
        'isotope_column': 'The name of the isotope column.',
        'isotopolog_column': 'The name of the isotopolog column.',
        'gradient_position_column': 'The name of the gradient position column.',
        'gradient_pos_density_column': (
            'The name of the gradient position density column.'
        ),
        'gradient_pos_amt_column': (
            'The name of the gradient position amount column.'
        ),
    },
    output_descriptions={
        'standardized_metadata': 'The standardized qSIP2 metadata.'
    },
    name='Standardize qSIP2 metadata.',
    description=(
        'Standardizes and validates qSIP2 metadata by ensuring all requisite '
        'variables are present, renaming variables to standardized names, and '
        'combining separate source-level and sample-level metadata files, if '
        'present. If a variable is present in both sample-level and '
        'source-level metadata, the values in the sample-level metadata take '
        'precedence.'
    ),
    citations=[]
)

plugin.methods.register_function(
    function=calculate_weighted_average_densities,
    inputs={
        'table': FeatureTable[Frequency],
    },
    parameters={
        'metadata': Metadata,
    },
    outputs=[
        ('source_wads', SourceData[SourceWAD])
    ],
    input_descriptions={
        'table': 'Your feature table.'
    },
    parameter_descriptions={
        'metadata': 'Your standardized metadata.'
    },
    output_descriptions={
        'source_wads': 'The per-source weighted average densities.'
    },
    name='Calculate weighted average densities.',
    description='Calculate per-source weighted average densities.',
    citations=[]
)

plugin.visualizers.register_function(
    function=plot_weighted_average_densities,
    inputs={
        'source_wads': SourceData[SourceWAD],
    },
    parameters={
        'metadata': Metadata,
        'group': Str,
    },
    input_descriptions={
        'source_wads': 'The per-source weighted average density values.'
    },
    parameter_descriptions={
        'metadata': 'The standardized metdata',
        'group': 'A source-level metadata column used to facet the plot.',
    },
    name='Plot weighted average densities.',
    description=(
        'Plots the per-source weighted average density values, colored by '
        'isotope and optionally faceted by the source-level metadata column '
        'specified by `group`.'
    ),
    citations=[],
)

plugin.visualizers.register_function(
    function=plot_sample_curves,
    inputs={
        'table': FeatureTable[Frequency],
    },
    parameters={
        'metadata': Metadata,
    },
    input_descriptions={
        'table': 'The feature table.',
    },
    parameter_descriptions={
        'metadata': 'The standardized metadata.',
    },
    name='Plot per-source density curves.',
    description=(
        'Plot gradient position by normalized relative feature abundance, '
        'faceted by source.'
    ),
    citations=[],
)

plugin.visualizers.register_function(
    function=plot_density_outliers,
    inputs={},
    parameters={
        'metadata': Metadata
    },
    input_descriptions={},
    parameter_descriptions={
        'metadata': 'The standardized qSIP2 metadata.'
    },
    name='Plot per-source density outliers.',
    description=(
        'Plots gradient position by density, faceted by source, to aid in the '
        'detection of density outliers.'
    ),
    citations=[],
)

plugin.methods.register_function(
    function=filter_by_prevalence,
    inputs={
        'table': FeatureTable[Frequency]
    },
    parameters={
        'metadata': Metadata,
        'unlabeled_isotope': Str,
        'labeled_isotope': Str,
        'min_unlabeled_sources': Int,
        'min_labeled_sources': Int,
        'min_unlabeled_fractions': Int,
        'min_labeled_fractions': Int
    },
    outputs=[
        ('filtered_table', FeatureTable[RelativeFrequency]),
        ('feature_wads', FeatureData[FeatureWAD])
    ],
    input_descriptions={
        'table': 'The feature table.'
    },
    parameter_descriptions={
        'metadata': 'The standardized qSIP2 metadata.',
        'unlabeled_isotope': (
            'The value of the isotope variable that represents the unlabeled '
            'isotope.'
        ),
        'labeled_isotope': (
            'The value of the isotope variable that represents the labeled '
            'isotope.'
        ),
        'min_unlabeled_sources': (
            'The minimum number of unlabeled sources a feature must be '
            'present in to be retained.'
        ),
        'min_labeled_sources': (
            'The minimum number of labeled sources a feature must be present '
            'in to be retained.'
        ),
        'min_unlabeled_fractions': (
            'The minimum number of fractions a feature must be present in '
            'to be considered present in an unlabeled source.'
        ),
        'min_labeled_fractions': (
            'The minimum number of fractions a feature must be present in '
            'to be considered present in a labeled source.'
        )
    },
    output_descriptions={
        'filtered_table': 'The filtered relative abundance feature table.',
        'feature_wads': (
            'The filtered per-feature weighted average densities.'
        )
    },
    name='Filter features by source and fraction prevalence.',
    description=(
        'Filter features by source and fraction prevalence to prepare for '
        'analysis.'
    ),
    citations=[]
)

plugin.methods.register_function(
    function=calculate_excess_atom_fractions,
    inputs={
        'table': FeatureTable[RelativeFrequency],
        'feature_wads': FeatureData[FeatureWAD],
    },
    parameters={
        'metadata': Metadata,
        'unlabeled_isotope': Str,
        'labeled_isotope': Str,
        'resamples': Int,
        'random_seed': Int,
        'allow_resampling_failures': Bool,
    },
    outputs=[
        ('excess_atom_fractions', FeatureData[EAF])
    ],
    input_descriptions={
        'table': 'The prevalence-filtered feature table.',
        'feature_wads': 'The per-feature weighted average densities.',
    },
    parameter_descriptions={
        'metadata': 'The standardized qSIP2 metadata.',
        'unlabeled_isotope': (
            'The value of the isotope variable that represents the unlabeled '
            'isotope.'
        ),
        'labeled_isotope': (
            'The value of the isotope variable that represents the labeled '
            'isotope.'
        ),
        'resamples': 'The number of bootstrap resamplings to perform.',
        'random_seed': 'The random seed to use during resampling.',
        'allow_resampling_failures': (
            'Whether to allow bootstrapped per-feature weighted average '
            'density vectors that contain all-NA values. If True then such '
            'samples are silentlly discarded, if False then an error is '
            'raised.'
        )
    },
    output_descriptions={
        'excess_atom_fractions': ('The per-feature excess atom fractions.'),
    },
    name='Calculate excess atom fractions (EAFs).',
    description=(
        'Placeholder.'
    ),
    citations=[]
)


plugin.visualizers.register_function(
    function=plot_excess_atom_fractions,
    inputs={
        'excess_atom_fractions': FeatureData[EAF],
    },
    parameters={
        'num_top': Int,
        'confidence_interval': Float
    },
    input_descriptions={
        'excess_atom_fractions': 'The per-feature excess atom fraction values.',
    },
    parameter_descriptions={
        'num_top': (
            'The number of taxa displayed, selected in order of decreasing '
            'excess atom fraction.'
        ),
        'confidence_interval': (
            'The confidence interval to display from the bootstrapped excess '
            'atom fractions.'
        )
    },
    name='Visualize per-feature excess atom fractions.',
    description=(
        'Plots per-taxon excess atom fractions with bootstrapped confidence '
        'intervals.'
    ),
    citations=[]
)


importlib.import_module('q2_qsip2.types._deferred_setup')
