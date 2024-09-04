# ----------------------------------------------------------------------------
# Copyright (c) 2024, Colin Wood.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import importlib

from qiime2.plugin import Bool, Citations, Metadata, Plugin, Str
from q2_types.feature_table import FeatureTable, Frequency

from q2_qsip2 import __version__
from q2_qsip2.workflow import standard_workflow, generate_qsip_metadata
from q2_qsip2.types import QSIP2Metadata


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
        'qsip_metadata': QSIP2Metadata,
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
    function=generate_qsip_metadata,
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
        ('qsip_metadata', QSIP2Metadata)
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
        'qsip_metadata': 'Placeholder.'
    },
    name='Process and combine qSIP metadata',
    description=(
        'Placeholder.'
    )
)

importlib.import_module('q2_qsip2.types._deferred_setup')
