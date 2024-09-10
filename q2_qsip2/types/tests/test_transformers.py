# ----------------------------------------------------------------------------
# Copyright (c) 2024, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import pandas as pd
from pandas.testing import assert_frame_equal
import rpy2.robjects as ro
from rpy2.robjects.methods import RS4

import importlib.resources
import pickle

import qiime2
from qiime2.plugin.testing import TestPluginBase

from q2_qsip2.types import QSIP2DataFormat


class TestTransformers(TestPluginBase):
    package = 'q2_qsip2.types.tests'

    def get_qsip_object(self):
        pickle_fp = (
            importlib.resources.files(__package__) /
            'data' / 'qsip-data.pickle'
        )

        transformer = self.get_transformer(QSIP2DataFormat, RS4)

        return transformer(QSIP2DataFormat(pickle_fp, mode='r'))

    def test_object_to_pickle_file_and_back(self):
        from_object_transformer = self.get_transformer(RS4, QSIP2DataFormat)
        from_format_transformer = self.get_transformer(QSIP2DataFormat, RS4)

        qsip_object = self.get_qsip_object()
        round_trip_qsip_object = from_format_transformer(
            from_object_transformer(qsip_object)
        )

        self.assertEqual(
            pickle.dumps(qsip_object), pickle.dumps(round_trip_qsip_object)
        )
