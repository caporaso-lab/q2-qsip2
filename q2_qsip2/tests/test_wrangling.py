# ----------------------------------------------------------------------------
# Copyright (c) 2024, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import pandas as pd

import qiime2
from qiime2.plugin.testing import TestPluginBase

from q2_qsip2._wrangling import (
    _extract_source_metadata, _validate_metadata_columns
)


class WranglingTests(TestPluginBase):
    package = 'q2_qsip2.tests'

    def sample_metadata(self):
        df = pd.DataFrame({
            'sample-id': ['a', 'b', 'c', 'd'],
            'source-id': ['s1', 's2', 's1', 's2'],
            'sample-level-data': ['w', 'x', 'y', 'z'],
            'source-level-data': ['x', 'y', 'x', 'y'],
        })
        df.set_index('sample-id', inplace=True)

        return qiime2.Metadata(df)

    def test_extract_source_metadata(self):
        extracted = _extract_source_metadata(
            self.sample_metadata(), 'source-id'
        ).to_dataframe().reset_index()

        # only rows that have a unique 'source-id' are retained; only
        # source-level columns are retained
        exp = pd.DataFrame({
            'id': ['s1', 's2'],
            'source-level-data': ['x', 'y'],
        })

        self.assertTrue(exp.equals(extracted))

    def metadata_to_validate(self):
        df = pd.DataFrame({
            'sample-id': ['a', 'b', 'c', 'd'],
            'isotope': ['12C', '12C', '13C', '13C'],
            'my-isotopolog-col': ['glucose', 'glucose', 'glucose', 'glucose'],
        })
        df.set_index('sample-id', inplace=True)

        return qiime2.Metadata(df)

    def metadata_column_mapping(self):
        return {
            'isotope': None,
            'isotopolog': 'my-isotopolog-col',
        }

    def test_validate_metadata_columns(self):
        metadata = self.metadata_to_validate()
        columns_mapping = self.metadata_column_mapping()

        _validate_metadata_columns(metadata, columns_mapping, 'source')

    def metadata_column_mapping_missing_default(self):
        return {
            'isotope': None,
            'isotopolog': 'my-isotopolog-col',
            'amount': None,
        }

    def test_validate_metadata_columns_missing_default(self):
        metadata = self.metadata_to_validate()
        columns_mapping = self.metadata_column_mapping_missing_default()

        exp_error = (
           'The following required columns were not found in the '
           'source metadata:\n\n'
           f'{"Default":^25} | {"Provided":^25}\n'
           f'{"-" * 23:^25} | {"-" * 23:^25}'
           f'\n{"amount":^25} | {"N/A (default used)":^25}'
           '\n\nPlease update the column names passed to the method '
           'or update your metadata to use the defaults.'
        )

        with self.assertRaisesRegex(ValueError, exp_error):
            _validate_metadata_columns(metadata, columns_mapping, 'source')

    def metadata_column_mapping_missing_provided(self):
        return {
            'isotope': None,
            'isotopolog': 'my-isotopolog-col',
            'amount': 'my-amount-col',
        }

    def test_validate_metadata_columns_missing_provided(self):
        metadata = self.metadata_to_validate()
        columns_mapping = self.metadata_column_mapping_missing_provided()

        exp_error = (
           'The following required columns were not found in the '
           'source metadata:\n\n'
           f'{"Default":^25} | {"Provided":^25}\n'
           f'{"-" * 23:^25} | {"-" * 23:^25}'
           f'\n{"amount":^25} | {"my-amount-col":^25}'
           '\n\nPlease update the column names passed to the method '
           'or update your metadata to use the defaults.'
        )

        with self.assertRaisesRegex(ValueError, exp_error):
            _validate_metadata_columns(metadata, columns_mapping, 'source')
