"""
Copyright 2017 Arm Ltd.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

SPDX-License-Identifier: Apache-2.0
"""

import os
from setuptools import find_packages, setup
import sys


os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path = ['src'] + sys.path

import advisor

with open('README.md') as f:
    long_description = f.read()

setup(
    name=advisor.__project__,
    version=advisor.__version__,
    url=advisor.__webpage__,
    license='Apache-2.0',
    description=advisor.__summary__,
    long_description=long_description,
    author='Chris January',
    author_email='chris.january@arm.com',
    packages=find_packages('src'),
    package_dir={'advisor': 'src/advisor'},
    package_data={'advisor': ['templates/*.html',
                              'local/en/LC_MESSAGES/advisor.mo']},
    entry_points={
        'console_scripts': [
            '%s = advisor:main' % advisor.__project__,
        ],
    },
    install_requires=[
        'jinja2',
    ],
    zip_safe=False  # gettext.Catalog is not zip-safe.
)
