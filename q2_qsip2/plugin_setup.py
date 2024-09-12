# ----------------------------------------------------------------------------
# Copyright (c) 2024, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import importlib

from qiime2.plugin import Bool, Citations, List, Metadata, Plugin, Str
from q2_types.feature_table import FeatureTable, Frequency

from q2_qsip2 import __version__
from q2_qsip2.workflow import standard_workflow, create_qsip_data
from q2_qsip2.types import QSIP2Data
from q2_qsip2.visualizers._visualizers import (
    plot_weighted_average_densities, plot_sample_curves, plot_density_outliers,
    show_comparison_groups
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
    # TODO
    citations=[citations['Caporaso-Bolyen-2024']]
)

plugin.methods.register_function(
    function=standard_workflow,
    inputs={
        'table': FeatureTable[Frequency],
        'qsip_metadata': QSIP2Data,
    },
    parameters={},
    outputs=[
        ('output_table', FeatureTable[Frequency])
    ],
    input_descriptions={
        'table': 'The feature table.',
        'qsip_metadata': 'The qSIP metadata.',
    },
    parameter_descriptions={},
    output_descriptions={
        'output_table': 'Placeholder.'
    },
    name='Run the standard qSIP2 workflow.',
    description=(
        'Placeholder.'
    )
)

plugin.methods.register_function(
    function=create_qsip_data,
    inputs={
        'table': FeatureTable[Frequency]
    },
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
        ('qsip_data', QSIP2Data)
    ],
    input_descriptions={},
    parameter_descriptions={
        'sample_metadata': 'The sample-level metadata.',
        'source_metadata': 'The source-level metadata.',
        'source_mat_id_column': 'The name of the source id column.',
        'isotope_column': 'The name of the isotope column.',
        'isotopolog_column': 'The name of the isotopolog column.',
        'gradient_position_column': 'The name of the gradient position column.',
        'gradient_pos_density_column': 'The name of the density column.',
        'gradient_pos_amt_column': 'The name of the amount column.',
    },
    output_descriptions={
        'qsip_data': 'Placeholder.'
    },
    name='Bundle your qSIP metadata and feature table.',
    description=(
        'Placeholder.'
    )
)

plugin.visualizers.register_function(
    function=plot_weighted_average_densities,
    inputs={
        'qsip_data': QSIP2Data
    },
    parameters={
        'group': Str
    },
    input_descriptions={
        'qsip_data': 'The qSIP data for which to plot the weighted average '
                     'densities.'
    },
    parameter_descriptions={
        'group': 'A source-level metadata column used to facet the plot.'
    },
    name='Plot weighted average densities.',
    description=(
        'Plots the per-source weighted average density, colored by isotope '
        'and optionally faceted by the source-level metadata column `group`.'
    ),
    citations=[],
)

plugin.visualizers.register_function(
    function=plot_sample_curves,
    inputs={
        'qsip_data': QSIP2Data
    },
    parameters={},
    input_descriptions={
        'qsip_data': 'The qsip data artifact.'
    },
    parameter_descriptions={},
    name='Plot per-source density curves.',
    description=(
        'Plots gradient position by relative amount of DNA, faceted by source.'
    ),
    citations=[],
)

plugin.visualizers.register_function(
    function=plot_density_outliers,
    inputs={
        'qsip_data': QSIP2Data
    },
    parameters={},
    input_descriptions={
        'qsip_data': 'The qsip data artifact.'
    },
    parameter_descriptions={},
    name='Plot per-source density outliers.',
    description=(
        'Plots gradient position by density, faceted by source, and performs '
        'Cook\'s outlier detection.'
    ),
    citations=[],
)

plugin.visualizers.register_function(
    function=show_comparison_groups,
    inputs={
        'qsip_data': QSIP2Data
    },
    parameters={
        'groups': List[Str]
    },
    input_descriptions={
        'qsip_data': 'The qsip data artifact.'
    },
    parameter_descriptions={
        'groups': 'The names of one or more source-level metadata columns used '
                  'to further subdivide the labeled and unlabeled samples.'
    },
    name='Show available comparison groupings.',
    description=(
        'Displays a table of source-level ids grouped in columns by isotope '
        'and in rows by the given groups.'
    ),
    citations=[],
)

importlib.import_module('q2_qsip2.types._deferred_setup')
