import importlib

from q2_qsip2.plugin_setup import plugin
from q2_qsip2.types import (
    QSIP2Data, QSIP2DataFormat, QSIP2DataDirectoryFormat
)


plugin.register_semantic_types(QSIP2Data)

plugin.register_formats(
    QSIP2DataFormat, QSIP2DataDirectoryFormat
)

plugin.register_artifact_class(
    QSIP2Data,
    directory_format=QSIP2DataDirectoryFormat,
    description="A serialized qSIP2 data object."
)

importlib.import_module('._transformers', __name__)
