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

import io
import unittest
from advisor.makefile_scanner import MakefileScanner
from advisor.report import Report


class TestMakefileScanner(unittest.TestCase):
    def test_accepts_file(self):
        makefile_scanner = MakefileScanner()
        self.assertFalse(makefile_scanner.accepts_file('test'))
        self.assertTrue(makefile_scanner.accepts_file('Makefile'))
        self.assertTrue(makefile_scanner.accepts_file('Makefile.in'))
        self.assertTrue(makefile_scanner.accepts_file('Makefile.am'))

    def test_scan_file_object(self):
        makefile_scanner = MakefileScanner()
        report = Report('/root')
        io_object = io.StringIO('xxx')
        makefile_scanner.scan_file_object(
            'Makefile', io_object, report)
        self.assertEquals(len(report.issues), 0)
        report = Report('/root')
        io_object = io.StringIO('-lotherarch')
        makefile_scanner.scan_file_object(
            'Makefile', io_object, report)
        self.assertEquals(len(report.issues), 1)
