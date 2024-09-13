# ----------------------------------------------------------------------------
# Copyright (c) 2024, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from rpy2.robjects.methods import RS4

import pickle

from q2_qsip2.plugin_setup import plugin
from q2_qsip2.types import (
    QSIP2DataUnfilteredFormat, QSIP2DataFilteredFormat, QSIP2DataEAFFormat
)


def _format_to_qsip_object(ff):
    with ff.open() as fh:
        qsip_object = pickle.load(fh)

    return qsip_object


def _qsip_object_to_format(qsip_object, ff):
    with ff.open() as fh:
        pickle.dump(qsip_object, fh)

    return ff


@plugin.register_transformer
def _1(qsip_object: RS4) -> QSIP2DataUnfilteredFormat:
    ff = QSIP2DataUnfilteredFormat()
    return _qsip_object_to_format(qsip_object, ff)


@plugin.register_transformer
def _2(ff: QSIP2DataUnfilteredFormat) -> RS4:
    return _format_to_qsip_object(ff)


@plugin.register_transformer
def _3(qsip_object: RS4) -> QSIP2DataFilteredFormat:
    ff = QSIP2DataFilteredFormat()
    return _qsip_object_to_format(qsip_object, ff)


@plugin.register_transformer
def _4(ff: QSIP2DataFilteredFormat) -> RS4:
    return _format_to_qsip_object(ff)


@plugin.register_transformer
def _5(qsip_object: RS4) -> QSIP2DataEAFFormat:
    ff = QSIP2DataFilteredFormat()
    return _qsip_object_to_format(qsip_object, ff)


@plugin.register_transformer
def _6(ff: QSIP2DataEAFFormat) -> RS4:
    return _format_to_qsip_object(ff)
