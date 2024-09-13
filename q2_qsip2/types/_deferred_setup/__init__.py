# ----------------------------------------------------------------------------
# Copyright (c) 2024, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import importlib

from q2_qsip2.plugin_setup import plugin
from q2_qsip2.types._types import (
    QSIP2Data, Unfiltered, Filtered, EAF
)
from q2_qsip2.types._formats import (
    QSIP2DataUnfilteredFormat, QSIP2DataUnfilteredDirectoryFormat,
    QSIP2DataFilteredFormat, QSIP2DataFilteredDirectoryFormat,
    QSIP2DataEAFFormat, QSIP2DataEAFDirectoryFormat
)


plugin.register_semantic_types(QSIP2Data, Unfiltered, Filtered, EAF)

plugin.register_formats(
    QSIP2DataUnfilteredFormat, QSIP2DataUnfilteredDirectoryFormat,
    QSIP2DataFilteredFormat, QSIP2DataFilteredDirectoryFormat,
    QSIP2DataEAFFormat, QSIP2DataEAFDirectoryFormat
)

plugin.register_artifact_class(
    QSIP2Data[Unfiltered],
    directory_format=QSIP2DataUnfilteredDirectoryFormat,
    description=(
        'Represents initial imported qSIP2 data, containing source- and '
        'sample-level metadata and a feature table.'
    )
)

plugin.register_artifact_class(
    QSIP2Data[Filtered],
    directory_format=QSIP2DataFilteredDirectoryFormat,
    description=(
        'Represents filtered qSIP2 data, containg labeled and unlabeled '
        'sources that constitute a desired comparison.'
    )
)

plugin.register_artifact_class(
    QSIP2Data[EAF],
    directory_format=QSIP2DataEAFDirectoryFormat,
    description=(
        'Represents fully process qSIP2 data that has been resampled and '
        'had excess atom fractions (EAF) calculated.'
    )
)

importlib.import_module('._transformers', __name__)
