# ----------------------------------------------------------------------------
# Copyright (c) 2024, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import pandas as pd

from q2_qsip2.plugin_setup import plugin
from q2_qsip2.types import QSIP2SourceWADsFormat


@plugin.register_transformer
def _1(df: pd.DataFrame) -> QSIP2SourceWADsFormat:
    ff = QSIP2SourceWADsFormat()
    with ff.open() as fh:
        df.to_csv(fh, sep='\t', index=False)

    return ff


@plugin.register_transformer
def _2(ff: QSIP2SourceWADsFormat) -> pd.DataFrame:
    with ff.open() as fh:
        df = pd.read_csv(fh, sep='\t')

    return df
