# ----------------------------------------------------------------------------
# Copyright (c) 2024, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import rpy2.robjects as ro

import pickle

from qiime2.plugin import ValidationError
import qiime2.plugin.model as model


# TODO: communicate warning about using pickled data
class QSIP2DataFormatBase(model.BinaryFileFormat):
    package = 'q2_qsip2.types.tests'

    def stage_specific_validation_method(self, qsip_data_obj):
        pass

    def _validate_(self, level):
        with self.open() as fh:
            qsip_data_obj = pickle.load(fh)

        try:
            ro.r['validate'](qsip_data_obj)
            self.stage_specific_validation_method(qsip_data_obj)
        except Exception as e:
            msg = (
                'There was a problem loading your qSIP2 data. See the below '
                f'error message for more detail.\n{str(e)}\n'
            )
            raise ValidationError(msg)


class QSIP2DataUnfilteredFormat(QSIP2DataFormatBase):
    def stage_specific_validation_method(self, qsip_data_obj):
        # TODO: update once implemented in R
        pass


QSIP2DataUnfilteredDirectoryFormat = model.SingleFileDirectoryFormat(
    'QSIP2DataUnfilteredDirectoryFormat',
    'qsip-data.pickle',
    QSIP2DataUnfilteredFormat
)


class QSIP2DataFilteredFormat(QSIP2DataFormatBase):
    def stage_speicif_validation_method(self, qsip_data_obj):
        # TODO: update once implemented in R
        pass


QSIP2DataFilteredDirectoryFormat = model.SingleFileDirectoryFormat(
    'QSIP2DataFilteredDirectoryFormat',
    'qsip-data.pickle',
    QSIP2DataFilteredFormat
)


class QSIP2DataEAFFormat(QSIP2DataFormatBase):
    def stage_specific_validation_method(self, qsip_data_obj):
        # TODO: update once implemented in R
        pass


QSIP2DataEAFDirectoryFormat = model.SingleFileDirectoryFormat(
    'QSIP2DataEAFDirectoryFormat',
    'qsip-data.pickle',
    QSIP2DataEAFFormat
)
