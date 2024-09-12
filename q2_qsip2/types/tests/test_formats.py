# ----------------------------------------------------------------------------
# Copyright (c) 2024, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import biom
import pandas as pd
import rpy2.robjects as ro
from rpy2.robjects.methods import RS4

import importlib.resources
from pathlib import Path
import pickle
import tempfile

import qiime2
from qiime2.plugin import ValidationError
from qiime2.plugin.testing import TestPluginBase

from q2_qsip2.types import QSIP2DataFormat
from q2_qsip2.workflow import create_qsip_data


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

    def test_valid_QSIP2DataFormat_from_files(self):
        source_md = self.get_source_metadata()
        sample_md = self.get_sample_metadata()
        table = self.get_feature_table()

        qsip_object = create_qsip_data(table, sample_md, source_md)

        transformer = self.get_transformer(
            RS4, QSIP2DataFormat
        )
        format = transformer(qsip_object)

        format.validate()

    def test_valid_QSIP2DataFormat_from_pickle(self):
        pickle_fp = (
            importlib.resources.files(__package__) /
            'data' / 'qsip-data.pickle'
        )

        format = QSIP2DataFormat(pickle_fp, mode='r')

        format.validate()

    def test_invalid_QSIP2DataFormat(self):
        # create useless rpy2 object to pickle
        vector = ro.r("c('Q', 'I', 'I', 'M', 'E', '2')")

        with tempfile.TemporaryDirectory() as tempdir:
            fp = Path(tempdir) / 'qsip-data.pickle'

            with open(fp, 'wb') as fh:
                pickle.dump(vector, fh)

            format = QSIP2DataFormat(fp, mode='r')

            msg = 'There was a problem loading your qSIP2 data.*'
            with self.assertRaisesRegex(ValidationError, msg):
                format.validate()
