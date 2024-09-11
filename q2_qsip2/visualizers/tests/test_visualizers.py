# ----------------------------------------------------------------------------
# Copyright (c) 2024, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from qiime2.plugin.testing import TestPluginBase

from q2_qsip2.visualizers._visualizers import plot_weighted_average_density

class VisualizerTests(TestPluginBase):
    package = 'q2_qsip2.visualizers.tests'

    def test_weighted_average_density_visualizer(self):
        pass
