import pandas as pd
from rpy2.robjects.methods import RS4

import pickle

import qiime2

from q2_qsip2.plugin_setup import plugin
from q2_qsip2.types import QSIP2DataFormat


@plugin.register_transformer
def _1(qsip_object: RS4) -> QSIP2DataFormat:
    ff = QSIP2DataFormat()
    with ff.open() as fh:
        pickle.dump(qsip_object, fh)

    return ff


@plugin.register_transformer
def _2(ff: QSIP2DataFormat) -> RS4:
    with ff.open() as fh:
        qsip_object = pickle.load(fh)

    return qsip_object
