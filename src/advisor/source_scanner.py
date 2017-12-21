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

from .compiler_specific_issue import CompilerSpecificIssue
from .inline_asm_issue import InlineAsmIssue
from .intrinsic_issue import IntrinsicIssue
from .intrinsics import INTRINSICS
from .naive_cpp import NaiveCpp, PreprocessorDirective
from .ported_inline_asm_remark import PortedInlineAsmRemark
from .pragma_simd_issue import PragmaSimdIssue
from .preprocessor_error_issue import PreprocessorErrorIssue
from .scanner import Scanner


class SourceScanner(Scanner):
    """Scanner that scans C, C++ and Fortran source files for potential porting
    issues."""

    SOURCE_EXTENSIONS = ['.c', '.cc', '.cpp', '.cxx',
                         '.f', '.f77', '.f90', '.h',
                         '.hxx', '.hpp', '.i']

    INTRINSICS_RE_PROG = re.compile(r'(%s)' %
                                    '|'.join([(r'\b%s\b' % x) for x in INTRINSICS]))
    """Regular expression that matches architecture-specific intrinsics."""
    INLINE_ASM_RE_PROG = re.compile(
        r'(^|\s)(__asm__|asm)(\s+volatile)?(\s+goto)?\(')
    PRAGMA_SIMD_RE_PROG = re.compile(
        r'^\s*#\s*pragma\s+simd\s+')
    """ Regular expression that matches inline assembly."""

    # Regular expression to match #pragma simd directives.

    def __init__(self):
        self.ported_inline_asm = 0

    def accepts_file(self, filename):
        _, ext = os.path.splitext(filename)
        return ext.lower() in SourceScanner.SOURCE_EXTENSIONS

    def initialize_report(self, report):
        report.ported_inline_asm = 0

    def scan_file_object(self, filename, file_object, report):
        lineno = 0
        naive_cpp = NaiveCpp()
        found_aarch64_inline_asm = False
        inline_asm_issues = []
        preprocessor_errors = []
        continuation_line = None
        for lineno, line in enumerate(file_object, 1):
            if line.endswith('\\\n'):
                if continuation_line:
                    continuation_line += line
                else:
                    continuation_line = line
                continue
            elif continuation_line:
                line = continuation_line + line
                continuation_line = None
            if not line:
                continue
            result = naive_cpp.parse_line(line)
            if result.directive_type == PreprocessorDirective.TYPE_ERROR \
                    and not naive_cpp.in_other_arch_specific_code():
                preprocessor_errors.append(PreprocessorErrorIssue(filename,
                                                                  lineno,
                                                                  line.strip()))
            elif result.directive_type == PreprocessorDirective.TYPE_CONDITIONAL \
                    and result.is_compiler:
                if_line = result.if_line or line
                if if_line != line:
                    if_line = '%s /* %s */' % (line.strip(),
                                               if_line.strip())
                else:
                    if_line = if_line.strip()
                report.add_issue(CompilerSpecificIssue(
                                 filename, lineno, if_line.strip()))
            elif result.directive_type == PreprocessorDirective.TYPE_PRAGMA \
                    and SourceScanner.PRAGMA_SIMD_RE_PROG.search(line):
                report.add_issue(PragmaSimdIssue(
                    filename, lineno, line.strip()))
            elif not result.directive_type:
                if SourceScanner.INLINE_ASM_RE_PROG.search(line) and \
                    not '(""' in line and \
                        not '".symver ' in line:
                    if naive_cpp.in_aarch64_specific_code():
                        found_aarch64_inline_asm = True
                        report.ported_inline_asm += 1
                    else:
                        inline_asm_issues.append(
                            InlineAsmIssue(filename, lineno))
                if not naive_cpp.in_other_arch_specific_code():
                    match = SourceScanner.INTRINSICS_RE_PROG.search(line)
                    if match:
                        intrinsic = match.group(1)
                        report.add_issue(IntrinsicIssue(
                            filename, lineno, intrinsic))

        if not found_aarch64_inline_asm and inline_asm_issues:
            for issue in inline_asm_issues + preprocessor_errors:
                report.add_issue(issue)

    def finalize_report(self, report):
        if report.ported_inline_asm:
            report.add_remark(PortedInlineAsmRemark(report.ported_inline_asm))
