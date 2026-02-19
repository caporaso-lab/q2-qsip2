# ----------------------------------------------------------------------------
# Copyright (c) 2024, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import importlib

from q2_types.sample_data import SampleData
from q2_types.feature_data import FeatureData

from q2_qsip2.plugin_setup import plugin
from q2_qsip2.types._types import SourceData, FeatureWAD, SourceWAD, EAF
from q2_qsip2.types._formats import (
    QSIP2SourceWADsDirectoryFormat, QSIP2FeatureWADDirectoryFormat,
    QSIP2FeatureEAFDirectoryFormat,
)


plugin.register_semantic_types(SourceData, SourceWAD, FeatureWAD, EAF)


plugin.register_formats(
    QSIP2SourceWADsDirectoryFormat, QSIP2FeatureWADDirectoryFormat,
    QSIP2FeatureEAFDirectoryFormat,
)


plugin.register_artifact_class(
    SourceData[SourceWAD],
    directory_format=QSIP2SourceWADsDirectoryFormat,
    description=('Represents per-source weighted average density (WAD) values.')
)

plugin.register_artifact_class(
    FeatureData[FeatureWAD],
    directory_format=QSIP2FeatureWADDirectoryFormat,
    description=(
        'Represents per-feature weighted average density (WAD) values.'
    )
)

plugin.register_artifact_class(
    FeatureData[EAF],
    directory_format=QSIP2FeatureEAFDirectoryFormat,
    description=(
        'Represents per-feature excess atom fraction (EAF) values.'
    )
)

importlib.import_module('._transformers', __name__)
