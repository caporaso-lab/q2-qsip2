# ----------------------------------------------------------------------------
# Copyright (c) 2024, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from qiime2.plugin import SemanticType


QSIP2Data = SemanticType('QSIP2Data', field_names='stage')

Unfiltered = SemanticType('Unfiltered', variant_of=QSIP2Data.field['stage'])

Filtered = SemanticType('Filtered', variant_of=QSIP2Data.field['stage'])

EAF = SemanticType('EAF', variant_of=QSIP2Data.field['stage'])
