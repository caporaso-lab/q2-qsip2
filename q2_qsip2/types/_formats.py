# ----------------------------------------------------------------------------
# Copyright (c) 2024, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import pandas as pd
import rpy2.robjects as ro

import pickle

import qiime2
from qiime2.plugin import ValidationError
import qiime2.plugin.model as model


class QSIP2DataFormat(model.BinaryFileFormat):
    package = 'q2_qsip2.types.tests'

    def _validate_(self, level):
        with self.open() as fh:
            qsip_data_obj = pickle.load(fh)

        try:
            # TODO: why not implemented in R package?
            ro.r['validate'](qsip_data_obj)
        except Exception as e:
            msg = (
                'There was a problem loading your qSIP2 data. See the below '
                f'error message for more detail.\n{str(e)}\n'
            )
            raise ValidationError(msg)


QSIP2DataDirectoryFormat = model.SingleFileDirectoryFormat(
    'QSIP2DataDirectoryFormat', 'qsip-data.pickle', QSIP2DataFormat
)
