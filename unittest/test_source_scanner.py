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

from advisor.report import Report
from advisor.report_item import ReportItem
from advisor.source_scanner import SourceScanner
import io
import unittest


class TestSourceScanner(unittest.TestCase):
    def test_accepts_file(self):
        source_scanner = SourceScanner()
        self.assertFalse(source_scanner.accepts_file('test'))
        self.assertTrue(source_scanner.accepts_file('test.c'))
        self.assertTrue(source_scanner.accepts_file('test.cc'))
        self.assertTrue(source_scanner.accepts_file('test.CC'))
        self.assertTrue(source_scanner.accepts_file('test.f90'))
        self.assertTrue(source_scanner.accepts_file('test.F'))

    def test_scan_file_object(self):
        source_scanner = SourceScanner()

        report = Report('/root')
        io_object = io.StringIO('xxx')
        source_scanner.scan_file_object(
            'test.c', io_object, report)
        self.assertEquals(len(report.issues), 0)

        report = Report('/root')
        io_object = io.StringIO('__asm__("")')
        source_scanner.scan_file_object(
            'test.c', io_object, report)
        self.assertEquals(len(report.issues), 0)

        report = Report('/root')
        io_object = io.StringIO('__asm__("mov r0, r1")')
        source_scanner.scan_file_object(
            'test.c', io_object, report)
        self.assertEquals(len(report.issues), 1)

        report = Report('/root')
        io_object = io.StringIO('_otherarch_intrinsic_xyz(123)')
        source_scanner.scan_file_object(
            'test.c', io_object, report)
        self.assertEquals(len(report.issues), 1)

        report = Report('/root')
        io_object = io.StringIO('#pragma simd foo')
        source_scanner.scan_file_object(
            'test.c', io_object, report)
        self.assertEquals(len(report.issues), 1)
        self.assertEquals(report.issues[0].item_type, ReportItem.NEUTRAL)
