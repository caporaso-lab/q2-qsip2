# ----------------------------------------------------------------------------
# Copyright (c) 2024, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import biom
import pandas as pd

import importlib.resources

import qiime2
from qiime2.plugin.testing import TestPluginBase


class TestFormats(TestPluginBase):
    package = 'q2_qsip2.types.tests'

    def get_source_metadata(self):
        fp = importlib.resources.files(__package__) / 'data' / 'source.tsv'
        df = pd.read_csv(fp, sep='\t', index_col=0)

        return qiime2.Metadata(df)

    def get_sample_metadata(self):
        fp = importlib.resources.files(__package__) / 'data' / 'sample.tsv'
        df = pd.read_csv(fp, sep='\t', index_col=0)

        return qiime2.Metadata(df)

    def get_feature_table(self):
        fp = importlib.resources.files(__package__) / 'data' / 'feature.tsv'
        df = pd.read_csv(fp, sep='\t', index_col=0)

        return biom.Table(
            df.values, observation_ids=df.index, sample_ids=df.columns
        )
