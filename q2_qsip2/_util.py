# ----------------------------------------------------------------------------
# Copyright (c) 2024-2026, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import pandas as pd


def _get_max_level(taxonomy: pd.DataFrame):
    return taxonomy['Taxon'].apply(lambda x: len(x.split(';'))).max()


def _add_collapsed_column(
    taxonomy: pd.DataFrame, level: int
) -> pd.DataFrame:
    max_level = _get_max_level(taxonomy)

    def _collapse(tax):
        tax = [x.strip() for x in tax.split(';')]
        if len(tax) < max_level:
            padding = ['__'] * (max_level - len(tax))
            tax.extend(padding)
        return '; '.join(tax[:level])

    taxonomy[f'Taxon at Level {level}'] = taxonomy['Taxon'].apply(_collapse)
