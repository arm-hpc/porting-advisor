"""
Copyright 2017-2019 Arm Ltd.

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
from .continuation_parser import ContinuationParser
from .find_port import find_port_file, is_aarch64_specific_file_name
from .inline_asm_issue import InlineAsmIssue
from .intrinsic_issue import IntrinsicIssue, AVX256IntrinsicIssue, AVX512IntrinsicIssue
from .intrinsics import ARM_INTRINSICS, OTHER_ARCH_INTRINSICS, AVX256_INTRINSICS, AVX512_INTRINSICS
from .naive_comment_parser import NaiveCommentParser
from .naive_cpp import NaiveCpp, PreprocessorDirective
from .naive_function_parser import NaiveFunctionParser
from .no_equivalent_inline_asm_issue import NoEquivalentInlineAsmIssue
from .no_equivalent_intrinsic_issue import NoEquivalentIntrinsicIssue
from .ported_inline_asm_remark import PortedInlineAsmRemark
from .pragma_simd_issue import PragmaSimdIssue
from .preprocessor_error_issue import PreprocessorErrorIssue
from .scanner import Scanner
from .report import*

class SourceScanner(Scanner):
    """Scanner that scans C, C++ and Fortran source files for potential porting
    issues."""

    SOURCE_EXTENSIONS = ['.c', '.cc', '.cpp', '.cxx',
                         '.f', '.f77', '.f90', '.h',
                         '.hxx', '.hpp', '.i']

    ARM_INTRINSICS_RE_PROG = re.compile(r'(%s)' %
                                    '|'.join([(r'\b%s\b' % x) for x in ARM_INTRINSICS]))
    OTHER_ARCH_INTRINSICS_RE_PROG = re.compile(r'(%s)' %
                                    '|'.join([(r'\b%s\b' % x) for x in OTHER_ARCH_INTRINSICS]))
    AVX256_ARCH_INTRINSICS_RE_PROG = re.compile(r'(%s)' %
                                    '|'.join([(r'\b%s\b' % x) for x in AVX256_INTRINSICS]))
    AVX512_ARCH_INTRINSICS_RE_PROG = re.compile(r'(%s)' %
                                    '|'.join([(r'\b%s\b' % x) for x in AVX512_INTRINSICS]))

    """Regular expression that matches architecture-specific intrinsics."""
    INLINE_ASM_RE_PROG = re.compile(
        r'(^|\s)(__asm__|asm)(\s+volatile)?(\s+goto)?\(')
    """Regular expression that matches inline assembly."""
    PRAGMA_SIMD_RE_PROG = re.compile(
        r'^\s*#\s*pragma\s+simd\s+')
    """Regular expression to match #pragma simd directives."""

    def __init__(self):
        self.ported_inline_asm = 0
        self.aarch64_intrinsic_inline_asm_files = set()
        """Files containing aarch64-specific intrinsics or inline assembly."""
        self.aarch64_intrinsic_inline_asm_functions = set()
        """Functions containing aarch64-specific intrinsics or ininline assembly."""
        self.aarch64_functions = set()
        """Functions containing aarch64-specific code or with an aarch64 version."""
        self.other_arch_intrinsic_inline_asm_files = {}
        """Files containing other architecture specific intrinsics or inline assembly."""
        self.other_arch_intrinsic_inline_asm_functions = {}
        """Functions containing other architecture specific intrinsics or inline assembly."""

    def accepts_file(self, filename):
        _, ext = os.path.splitext(filename)
        return ext.lower() in SourceScanner.SOURCE_EXTENSIONS

    def initialize_report(self, report):
        report.ported_inline_asm = 0

    """Function to generate csv file for AVX instructions"""
    def prepare_csv_file(self, filename, avx256_count_no, avx512_count_no, total_avx_no, report):
        if total_avx_no > 0 :
            report.avx256_data.append(avx256_count_no)
            report.avx512_data.append(avx512_count_no)
            report.total_data.append(total_avx_no)
            report.filename_data.append(filename)

    def scan_file_object(self, filename, file_object, report):
        continuation_parser = ContinuationParser()
        naive_cpp = NaiveCpp()
        comment_parser = NaiveCommentParser()
        function_parser = NaiveFunctionParser()

        found_aarch64_inline_asm = False
        inline_asm_issues = []
        preprocessor_errors = []

        avx256_count = 0 #count of AVX256 instructions
        avx512_count = 0 #count of AVX512 instructions
        total_avx_count = 0 #total count of AVX instructions

        for lineno, line in enumerate(file_object, 1):
            line = continuation_parser.parse_line(line)

            if not line:
                continue

            is_comment = comment_parser.parse_line(line)
            if is_comment:
                continue

            result = naive_cpp.parse_line(line)
            if result.directive_type == PreprocessorDirective.TYPE_ERROR \
                    and naive_cpp.in_other_arch_else_code():
                preprocessor_errors.append(PreprocessorErrorIssue(filename,
                                                                  lineno,
                                                                  line.strip(),
                                                                  function=function_parser.current_function))
            elif result.directive_type == PreprocessorDirective.TYPE_CONDITIONAL \
                    and result.is_compiler:
                if_line = result.if_line or line
                if if_line != line:
                    if_line = '%s /* %s */' % (line.strip(),
                                               if_line.strip())
                else:
                    if_line = if_line.strip()
                report.add_issue(CompilerSpecificIssue(
                                 filename, lineno, if_line.strip(),
                                 function=function_parser.current_function))
            elif result.directive_type == PreprocessorDirective.TYPE_PRAGMA \
                    and SourceScanner.PRAGMA_SIMD_RE_PROG.search(line):
                report.add_issue(PragmaSimdIssue(
                    filename, lineno, line.strip(),
                    function=function_parser.current_function))
            elif (result.directive_type == PreprocessorDirective.TYPE_DEFINE and result.body) \
                    or not result.directive_type:
                if result.directive_type == PreprocessorDirective.TYPE_DEFINE:
                    line = result.body
                    function = result.macro_name
                else:
                    function_parser.parse_line(line)
                    function = function_parser.current_function

                if naive_cpp.in_aarch64_specific_code() or is_aarch64_specific_file_name(filename):
                    if function:
                        self.aarch64_functions.add(function)

                if SourceScanner.INLINE_ASM_RE_PROG.search(line) and \
                    not '(""' in line and \
                        not '".symver ' in line:
                    if naive_cpp.in_aarch64_specific_code():
                        found_aarch64_inline_asm = True
                    else:
                        inline_asm_issues.append(
                            InlineAsmIssue(filename, lineno, function=function))
                    if naive_cpp.in_aarch64_specific_code() or is_aarch64_specific_file_name(filename):
                        self.aarch64_intrinsic_inline_asm_files.add(filename)
                        if function:
                            self.aarch64_intrinsic_inline_asm_functions.add(function)
                    else:
                        if not filename in self.other_arch_intrinsic_inline_asm_files:
                            self.other_arch_intrinsic_inline_asm_files[filename] = \
                                NoEquivalentInlineAsmIssue(filename, lineno)
                        if function and not function in self.other_arch_intrinsic_inline_asm_functions:
                            self.other_arch_intrinsic_inline_asm_functions[function] = \
                                NoEquivalentInlineAsmIssue(filename, lineno, function=function)

                arm_match = SourceScanner.ARM_INTRINSICS_RE_PROG.search(line)
                other_match = SourceScanner.OTHER_ARCH_INTRINSICS_RE_PROG.search(line)
                avx256_match = SourceScanner.AVX256_ARCH_INTRINSICS_RE_PROG.search(line)
                avx512_match = SourceScanner.AVX512_ARCH_INTRINSICS_RE_PROG.search(line)
                if other_match and not arm_match:
                    intrinsic = other_match.group(1)
                    if not naive_cpp.in_other_arch_specific_code():
                        if avx256_match:
                            avx256_count += 1
                            report.add_issue(AVX256IntrinsicIssue(
                                filename, lineno, intrinsic, function=function))
                        elif avx512_match:
                            avx512_count += 1
                            report.add_issue(AVX512IntrinsicIssue(
                                filename, lineno, intrinsic, function=function))
                        else:
                            report.add_issue(IntrinsicIssue(
                                filename, lineno, intrinsic, function=function))
                    if not filename in self.other_arch_intrinsic_inline_asm_files:
                        self.other_arch_intrinsic_inline_asm_files[filename] = \
                            NoEquivalentIntrinsicIssue(filename, lineno, intrinsic)
                    if function and not function in self.other_arch_intrinsic_inline_asm_functions:
                        self.other_arch_intrinsic_inline_asm_functions[function] = \
                            NoEquivalentIntrinsicIssue(filename, lineno, intrinsic, function=function)
                if arm_match:
                    self.aarch64_intrinsic_inline_asm_files.add(filename)
                    if function:
                        self.aarch64_intrinsic_inline_asm_functions.add(function)

        if not found_aarch64_inline_asm:
            for issue in inline_asm_issues:
                if not issue.function or not issue.function in self.aarch64_functions:
                    report.add_issue(issue)
        for issue in preprocessor_errors:
            report.add_issue(issue)

        total_avx_count = avx256_count + avx512_count
        self.prepare_csv_file(filename, avx256_count, avx512_count, total_avx_count, report)

    def finalize_report(self, report):
        for function in self.other_arch_intrinsic_inline_asm_functions:
            if function in self.aarch64_functions:
                if not function in self.aarch64_intrinsic_inline_asm_functions:
                    report.add_issue(self.other_arch_intrinsic_inline_asm_functions[function])
                else:
                    report.ported_inline_asm += 1
                issue = self.other_arch_intrinsic_inline_asm_functions[function]
                fname = issue.filename
                if fname in self.other_arch_intrinsic_inline_asm_files:
                    del self.other_arch_intrinsic_inline_asm_files[fname]
        for fname in self.other_arch_intrinsic_inline_asm_files:
            port_file = find_port_file(
                fname, report.source_files, report.source_dirs)
            if port_file and port_file not in self.aarch64_intrinsic_inline_asm_files:
                report.add_issue(self.other_arch_intrinsic_inline_asm_files[fname])
            else:
                report.ported_inline_asm += 1
        if report.ported_inline_asm:
            report.add_remark(PortedInlineAsmRemark(report.ported_inline_asm))
