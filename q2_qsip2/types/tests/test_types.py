# ----------------------------------------------------------------------------
# Copyright (c) 2024, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from qiime2.plugin.testing import TestPluginBase

from q2_qsip2.types import QSIP2Data, Unfiltered, Filtered, EAF


class TestTypes(TestPluginBase):
    package = 'q2_qsip2.types.tests'

    def test_QSIP2Data_types_registered(self):
        self.assertRegisteredSemanticType(QSIP2Data)
        self.assertRegisteredSemanticType(Unfiltered)
        self.assertRegisteredSemanticType(Filtered)
        self.assertRegisteredSemanticType(EAF)
