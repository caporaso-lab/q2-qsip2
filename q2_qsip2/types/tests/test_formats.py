# ----------------------------------------------------------------------------
# Copyright (c) 2024, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import pandas as pd
from pandas.testing import assert_frame_equal

from q2_qsip2.types._types import QSIP2Metadata
from qiime2.plugin import ValidationError
from qiime2.plugin.testing import TestPluginBase

from q2_qsip2.types import QSIP2MetadataFormat


class TestFormats(TestPluginBase):
    package = 'q2_qsip2.types.tests'

    def valid_metadata_df(self):
        return pd.DataFrame({
            'sample-id': ['s1', 's2', 's3', 's4'],
            'isotope': ['16O', '16O', '18O', '18O'],
            'isotopolog': ['water', 'water', 'water', 'water'],
            'gradient_position': [1, 2, 1, 2],
            'gradient_pos_density': [0.8, 0.7, 0.9, 0.8],
            'gradient_pos_amt': [100, 50, 110, 40],
            'source_mat_id': ['a', 'a', 'b', 'b'],
        })

    def test_valid_QSIP2MetadataFormat(self):
        df = self.valid_metadata_df()

        file_format = QSIP2MetadataFormat()
        with file_format.open() as fh:
            df.to_csv(fh, sep='\t')

        file_format.validate()

    def test_missing_column(self):
        df = self.valid_metadata_df()
        df = df.drop(columns=['isotope'])

        file_format = QSIP2MetadataFormat()
        with file_format.open() as fh:
            df.to_csv(fh, sep='\t')

        error_msg = (
            '.*one or more required columns that are missing.*'
            'isotope.*'
        )
        with self.assertRaisesRegex(ValidationError, error_msg):
            file_format.validate()

    def test_misnamed_column(self):
        df = self.valid_metadata_df()
        df = df.rename(columns={'gradient_pos_amt': 'gradient_pos_amount'})

        file_format = QSIP2MetadataFormat()
        with file_format.open() as fh:
            df.to_csv(fh, sep='\t')

        error_msg = (
            '.*one or more required columns that are missing.*'
            'gradient_pos_amt.*'
        )
        with self.assertRaisesRegex(ValidationError, error_msg):
            file_format.validate()
