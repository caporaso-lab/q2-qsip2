# ----------------------------------------------------------------------------
# Copyright (c) 2024, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import pickle

import rpy2.robjects as ro
import pandas as pd

from qiime2.plugin import ValidationError
import qiime2.plugin.model as model


class QSIP2SourceWADsFormat(model.TextFileFormat):
    def _validate_(self, level):
        with self.open() as fh:
            df = pd.read_csv(fh, sep='\t')

        if not ('source_mat_id' in df.columns and 'WAD' in df.columns):
            raise ValidationError(
                'Expected columns, "source_mat_id", "WAD" not both found.'
            )


QSIP2SourceWADsDirectoryFormat = model.SingleFileDirectoryFormat(
    'QSIP2SourceWADsDirectoryFormat',
    'source-wads.tsv',
    QSIP2SourceWADsFormat
)


class QSIP2FeatureWADsFormat(model.TextFileFormat):
    def _validate_(self, level):
        with self.open() as fh:
            df = pd.read_csv(fh, sep='\t')

        if not 'feature_id' in df.columns:
            raise ValidationError('Expected column "feature_id" not found.')


QSIP2FeatureWADsDirectoryFormat = model.SingleFileDirectoryFormat(
    'QSIP2FeatureWADsDirectoryFormat',
    'feature-wads.tsv',
    QSIP2FeatureWADsFormat
)
