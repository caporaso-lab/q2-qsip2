# ----------------------------------------------------------------------------
# Copyright (c) 2024, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from qiime2.plugin import SemanticType
from q2_types.feature_data import FeatureData


SourceData = SemanticType('SourceData', field_names='type')

SourceWAD = SemanticType('SourceWAD', variant_of=SourceData.field['type'])

FeatureWAD = SemanticType('FeatureWAD', variant_of=FeatureData.field['type'])

EAF = SemanticType('EAF', variant_of=FeatureData.field['type'])
