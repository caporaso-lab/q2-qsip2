# ----------------------------------------------------------------------------
# Copyright (c) 2024, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import importlib

from q2_types.sample_data import SampleData

from q2_qsip2.plugin_setup import plugin
from q2_qsip2.types._types import SourceWADs
from q2_qsip2.types._formats import QSIP2SourceWADsDirectoryFormat


plugin.register_semantic_types(SourceWADs)


plugin.register_formats(QSIP2SourceWADsDirectoryFormat)


plugin.register_artifact_class(
    SampleData[SourceWADs],
    directory_format=QSIP2SourceWADsDirectoryFormat,
    description=('Represents per-source weighted average density (WAD) values.')
)


importlib.import_module('._transformers', __name__)
