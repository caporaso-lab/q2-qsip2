# ----------------------------------------------------------------------------
# Copyright (c) 2024-2026, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import unittest

from rachis.sdk import usage

from q2_qsip2._examples import tutorial_runthrough


class UsageExampleTests(unittest.TestCase):
    def test_examples(self):
        use = usage.ExecutionUsage()
        tutorial_runthrough(use)
