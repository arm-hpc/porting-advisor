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

from advisor.other_issues_filter import OtherIssuesFilter

from .asm_source_scanner import AsmSourceScanner
from .config_guess_scanner import ConfigGuessScanner
from .makefile_scanner import MakefileScanner
from .port_filter import PortFilter
from .source_scanner import SourceScanner


class Scanners:
    """Set of scanners that may be used to scan for potential porting issues in
    files."""

    def __init__(self):
        self.scanners = [SourceScanner(),
                         AsmSourceScanner(),
                         ConfigGuessScanner(),
                         MakefileScanner()]
        self.filters = [PortFilter(),
                        OtherIssuesFilter()]

    """Initializes the given report for scanning.

    Args:
        report (Report): Report to initialize_report.
    """

    def initialize_report(self, report):
        for a_filter in self.filters:
            a_filter.initialize_report(report)
        for scanner in self.scanners:
            scanner.initialize_report(report)

    def finalize_report(self, report):
        """Finalizes the given report.

        Args:
            report (Report): Report to finalize_report.
        """
        for a_filter in self.filters:
            a_filter.finalize_report(report)
        for scanner in self.scanners:
            scanner.finalize_report(report)

    def __iter__(self):
        return self.scanners.__iter__()
