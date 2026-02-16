# ----------------------------------------------------------------------------
# Copyright (c) 2024, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from qiime2.plugin import SemanticType
from q2_types.sample_data import SampleData
from q2_types.feature_data import FeatureData


SourceWADs = SemanticType('SourceWADs', variant_of=SampleData.field['type'])

WADs = SemanticType('WADs', variant_of=FeatureData.field['type'])
