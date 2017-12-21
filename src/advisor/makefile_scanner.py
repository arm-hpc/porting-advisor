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
import re

from .arch_specific_library_issue import ArchSpecificLibraryIssue
from .arch_specific_libs import ARCH_SPECIFIC_LIBS
from .scanner import Scanner


class MakefileScanner(Scanner):
    """Scanner that scans Makefiles."""

    MAKEFILE_NAMES = ['Makefile', 'Makefile.in', 'Makefile.am']

    ARCH_SPECIFIC_LIBS_RE_PROG = re.compile(r'(%s)' %
                                            '|'.join([(r'-l%s\b' % x) for x in ARCH_SPECIFIC_LIBS]))

    def accepts_file(self, filename):
        return os.path.basename(filename) in MakefileScanner.MAKEFILE_NAMES

    def scan_file_object(self, filename, file, report):
        for lineno, line in enumerate(file, 1):
            match = MakefileScanner.ARCH_SPECIFIC_LIBS_RE_PROG.search(line)
            if match:
                lib_name = match.group(1)
                report.add_issue(ArchSpecificLibraryIssue(
                    filename, lineno + 1, lib_name))
