# ----------------------------------------------------------------------------
# Copyright (c) 2024, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import pandas as pd
from pandas.testing import assert_frame_equal

import qiime2
from qiime2.plugin.testing import TestPluginBase

from q2_qsip2.types import QSIP2MetadataFormat


class TestTransformers(TestPluginBase):
    package = 'q2_qsip2.types.tests'

    def metadata_df(self):
        return pd.DataFrame({
            'sample-id': ['s1', 's2', 's3', 's4'],
            'isotope': ['16O', '16O', '18O', '18O'],
            'isotopolog': ['water', 'water', 'water', 'water'],
            'gradient_position': [1, 2, 1, 2],
            'gradient_pos_density': [0.8, 0.7, 0.9, 0.8],
            'gradient_pos_amt': [100, 50, 110, 40],
            'source_mat_id': ['a', 'a', 'b', 'b'],
        })

    def metadata_df_types(self):
        # this is necessary because int64 types are getting converted to
        # float64 by qiime2.Metadata...
        return {
            'gradient_position': 'int64',
            'gradient_pos_amt': 'int64'
        }

    def qiime2_metadata(self):
        df = self.metadata_df()
        df.set_index('sample-id', inplace=True)

        return qiime2.Metadata(df)

    def qsip2_metadata(self):
        df = self.metadata_df()
        file_format = QSIP2MetadataFormat()
        with file_format.open() as fh:
            df.to_csv(fh, index=False, sep='\t')

        return file_format

    def test_qsip2_metadata_to_qiime2_metadata(self):
        transformer = self.get_transformer(
            QSIP2MetadataFormat, qiime2.Metadata
        )

        qsip2_md = self.qsip2_metadata()
        qiime2_md = transformer(qsip2_md)

        qsip2_md_df = qsip2_md._to_dataframe()
        qiime2_md_df = qiime2_md.to_dataframe().reset_index()
        qiime2_md_df = qiime2_md_df.astype(self.metadata_df_types())

        assert_frame_equal(qsip2_md_df, qiime2_md_df)

    def test_qiime2_metadata_qsip2_metadata(self):
        transformer = self.get_transformer(
            qiime2.Metadata, QSIP2MetadataFormat
        )

        qiime2_md = self.qiime2_metadata()
        qsip2_md = transformer(qiime2_md)

        qsip2_md_df = qsip2_md._to_dataframe()
        qiime2_md_df = qiime2_md.to_dataframe().reset_index()

        assert_frame_equal(qsip2_md_df, qiime2_md_df)
