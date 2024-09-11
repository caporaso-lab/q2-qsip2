# ----------------------------------------------------------------------------
# Copyright (c) 2024, QIIME2.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import rpy2.robjects as ro
from rpy2.robjects.packages import importr

import importlib.resources
from pathlib import Path
import shutil
import tempfile

ggplot2 = importr('ggplot2')

def _ggplot2_object_to_visualization(
    ggplot2_obj: object, output_dir: Path, width: int, height: int
) -> None:
    '''
    '''
    index = importlib.resources.files('q2_qsip2') / 'assets' / 'index.html'
    shutil.copy(index, output_dir)

    ggplot2.ggsave(
        filename=str(output_dir / 'figure.svg'),
        plot=ggplot2_obj,
        device='svg',
        width=width,
        height=height,
        # units='px'
    )
