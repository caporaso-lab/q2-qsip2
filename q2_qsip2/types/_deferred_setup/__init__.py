import importlib

from q2_qsip2.plugin_setup import plugin
from q2_qsip2.types import (
    QSIP2Metadata, QSIP2MetadataFormat, QSIP2MetadataDirectoryFormat
)


plugin.register_semantic_types(QSIP2Metadata)

plugin.register_formats(QSIP2MetadataFormat, QSIP2MetadataDirectoryFormat)

plugin.register_artifact_class(
    QSIP2Metadata,
    directory_format=QSIP2MetadataDirectoryFormat,
    description="Validated qSIP2 metadata."
)

importlib.import_module('._transformers', __name__)
