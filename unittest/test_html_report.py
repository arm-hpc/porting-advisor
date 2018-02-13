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

from advisor.config_guess_scanner import ConfigGuessScanner
from advisor.html_report import HtmlReport
from advisor.report_item import ReportItem
from advisor.source_scanner import SourceScanner
import io
import tempfile
import unittest


class TestHtmlReport(unittest.TestCase):
    def test_item_icons(self):
        config_guess_scanner = ConfigGuessScanner()
        source_scanner = SourceScanner()

        report = HtmlReport('/root')
        io_object = io.StringIO('__asm__("mov r0, r1")')
        source_scanner.scan_file_object(
            'test_negative.c', io_object, report)
        io_object = io.StringIO('#pragma simd foo')
        source_scanner.scan_file_object(
            'test_neutral.c', io_object, report)
        io_object = io.StringIO('aarch64:Linux')
        config_guess_scanner.scan_file_object(
            'config.guess', io_object, report)
        self.assertEquals(len(report.issues), 2)
        self.assertEquals(len(report.remarks), 1)
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as ofp:
            report.write(ofp)
            fname = ofp.name
            ofp.close()

            with open(fname) as ifp:
                for line in ifp:
                    if 'test_negative.c' in line:
                        self.assertIn('#negative', line)
                    elif 'test_neutral.c' in line:
                        self.assertIn('#neutral', line)
                    elif 'config.guess' in line:
                        self.assertIn('#positive', line)

    def test_item_order(self):
        config_guess_scanner = ConfigGuessScanner()
        source_scanner = SourceScanner()

        report = HtmlReport('/root')
        io_object = io.StringIO('__asm__("mov r0, r1")')
        source_scanner.scan_file_object(
            'test_negative.c', io_object, report)
        io_object = io.StringIO('#pragma simd foo')
        source_scanner.scan_file_object(
            'test_neutral.c', io_object, report)
        io_object = io.StringIO('aarch64:Linux')
        config_guess_scanner.scan_file_object(
            'config.guess', io_object, report)
        self.assertEquals(len(report.issues), 2)
        self.assertEquals(len(report.remarks), 1)
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as ofp:
            report.write(ofp)
            fname = ofp.name
            ofp.close()

            seenPositive=False
            seenNeutral=False
            seenNegative=False

            with open(fname) as ifp:
                for line in ifp:
                    if 'test_negative.c' in line:
                        self.assertTrue(seenPositive)
                        self.assertFalse(seenNeutral)
                        seenNegative = True
                    elif 'test_neutral.c' in line:
                        self.assertTrue(seenPositive)
                        self.assertTrue(seenNegative)
                        seenNeutral = True
                    elif 'config.guess' in line:
                        self.assertFalse(seenNeutral)
                        self.assertFalse(seenNegative)
                        seenPositive = True

    def test_heading(self):
        report = HtmlReport('/home/user/source/application-1.0')

        with tempfile.NamedTemporaryFile(mode='w', delete=False) as ofp:
            report.write(ofp)
            fname = ofp.name
            ofp.close()

            seenHeading=False

            with open(fname) as ifp:
                for line in ifp:
                    if 'Porting Readiness Report' in line:
                        self.assertIn('application-1.0', line)
                        seenHeading = True
            
            self.assertTrue(seenHeading)
