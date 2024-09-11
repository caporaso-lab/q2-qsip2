# ----------------------------------------------------------------------------
# Copyright (c) 2024, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import rpy2.robjects as ro
from rpy2.robjects.methods import RS4
from rpy2.robjects.packages import importr

from typing import Optional
from pathlib import Path

from q2_qsip2.visualizers._helpers import _ggplot2_object_to_visualization

qsip2 = importr('qSIP2')

def plot_weighted_average_density(
    output_dir: str, qsip_object: RS4, group: Optional[str] = None
) -> None:
    '''
    '''
    plot = qsip2.plot_source_wads(qsip_object, group=group)

    _ggplot2_object_to_visualization(
        plot, Path(output_dir), width=10, height=4
    )


def plot_sample_curves(output_dir: str, qsip_object: RS4) -> None:
    '''
    '''
    plot = qsip2.plot_sample_curves(qsip_object)

    _ggplot2_object_to_visualization(
        plot, Path(output_dir), width=10, height=10
    )
