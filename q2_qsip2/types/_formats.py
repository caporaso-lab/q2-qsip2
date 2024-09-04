import pandas as pd

import qiime2
from qiime2.plugin import ValidationError
import qiime2.plugin.model as model

from q2_qsip2._wrangling import ALL_COLUMNS


class QSIP2MetadataFormat(model.TextFileFormat):
    def _to_dataframe(self):
        return pd.read_csv(self.path, sep='\t')

    def _validate_(self, level):
        df = self._to_dataframe()

        missing_columns = set(ALL_COLUMNS) - set(df.columns)
        if missing_columns:
            msg = (
                'There are one or more required columns that are missing from '
                f'the qSIP2 metadata. The missing column(s): {missing_columns}.'
                'Please use the `generate_qsip_metadata` method to create a '
                'valid qSIP2 metadata artifact.'
            )
            raise ValidationError(msg)


QSIP2MetadataDirectoryFormat = model.SingleFileDirectoryFormat(
    'QSIP2MetadataDirectoryFormat', 'metadata.tsv', QSIP2MetadataFormat
)
