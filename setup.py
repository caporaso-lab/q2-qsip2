# ----------------------------------------------------------------------------
# Copyright (c) 2024, Colin Wood.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from setuptools import find_packages, setup

import versioneer

description = ("A template QIIME 2 plugin.")

setup(
    name="q2-qsip2",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    license="BSD-3-Clause",
    packages=find_packages(),
    author="Colin Wood",
    author_email="colin.wood@nau.edu",
    description=description,
    url="www.qiime2.org",
    entry_points={
        "qiime2.plugins": [
            "q2_qsip2="
            "q2_qsip2"
            ".plugin_setup:plugin"]
    },
    package_data={
        "q2_qsip2": ["citations.bib", "assets/index.html"],
        "q2_qsip2.tests": ["data/*"],
    },
    zip_safe=False,
)
