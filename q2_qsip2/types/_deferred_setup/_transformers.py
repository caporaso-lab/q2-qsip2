# ----------------------------------------------------------------------------
# Copyright (c) 2024, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import pandas as pd

from q2_qsip2.plugin_setup import plugin
from q2_qsip2.types import (
    QSIP2SourceWADsFormat, QSIP2FeatureWADFormat, QSIP2FeatureEAFFormat
)


def _format_to_df(ff) -> pd.DataFrame:
    with ff.open() as fh:
        df = pd.read_csv(fh, sep='\t')

    return df


def _df_to_format(df: pd.DataFrame, format):
    ff = format()
    with ff.open() as fh:
        df.to_csv(fh, sep='\t', index=False)

    return ff


@plugin.register_transformer
def _1(df: pd.DataFrame) -> QSIP2SourceWADsFormat:
    return _df_to_format(df, QSIP2SourceWADsFormat)


@plugin.register_transformer
def _2(ff: QSIP2SourceWADsFormat) -> pd.DataFrame:
    return _format_to_df(ff)


@plugin.register_transformer
def _3(df: pd.DataFrame) -> QSIP2FeatureWADFormat:
    return _df_to_format(df, QSIP2FeatureWADFormat)


@plugin.register_transformer
def _4(ff: QSIP2FeatureWADFormat) -> pd.DataFrame:
    return _format_to_df(ff)


@plugin.register_transformer
def _5(df: pd.DataFrame) -> QSIP2FeatureEAFFormat:
    return _df_to_format(df, QSIP2FeatureEAFFormat)


@plugin.register_transformer
def _6(ff: QSIP2FeatureEAFFormat) -> pd.DataFrame:
    _format_to_df(ff)
