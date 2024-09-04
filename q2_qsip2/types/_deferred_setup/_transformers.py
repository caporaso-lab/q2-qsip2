import pandas as pd

import qiime2

from q2_qsip2.plugin_setup import plugin
from q2_qsip2.types import QSIP2MetadataFormat


@plugin.register_transformer
def _1(md: qiime2.Metadata) -> QSIP2MetadataFormat:
    df = md.to_dataframe()
    ff = QSIP2MetadataFormat()
    with ff.open() as fh:
        df.to_csv(fh, sep='\t')

    return ff


@plugin.register_transformer
def _2(ff: QSIP2MetadataFormat) -> qiime2.Metadata:
    with ff.open() as fh:
        df = pd.read_csv(fh, sep='\t', index_col=0)

    return qiime2.Metadata(df)
