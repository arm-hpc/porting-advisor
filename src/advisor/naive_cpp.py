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

import re
from .arch_strings import *


class PreprocessorDirective:
    """Information about a preprocessor directive."""
    TYPE_CONDITIONAL = '#if'
    TYPE_ERROR = '#error'
    TYPE_PRAGMA = '#pragma'
    TYPE_OTHER = 'other'

    def __init__(self, directive_type, if_line=None, is_compiler=None):
        self.directive_type = directive_type
        self.if_line = if_line
        self.is_compiler = is_compiler


class NaiveCpp:
    """Naive C preprocessor. This class is used by SourceScanner to determine
    which source lines will/will not be compiled on aarch64 platorms."""

    TOKEN_PROG = re.compile(
        r'((?:!\s*)?defined\s*\(\s*\w+\s*\)|(?:!\s*)?\w+|\|\||\&\&|\(|\)|\s+)')
    """Regular expression to tokenize C preprocessor directives."""
    DEFINED_PROG = re.compile(r'(?:(!)\s*)?defined\s*\(\s*(\w+)\s*\)')
    """Regular expression to match (possibly negated) defined(macro)
    expressions."""
    MACRO_PROG = re.compile(r'(?:(!)\s*)?(\w+)')
    """Regular expression to match (possibly negated) macro expressions."""
    AARCH64_MACROS_RE_PROG = re.compile(r'(?:\w*_|^)(%s)(?:_\w*|$)' %
                                        '|'.join(AARCH64_ARCHS),
                                        re.IGNORECASE)
    """Regular expression to match aarch64 predefined macros."""
    NON_AARCH64_MACROS_RE_PROG = re.compile(r'(?:\w*_|^)(%s)(?:_\w*|$)' %
                                            '|'.join(NON_AARCH64_ARCHS),
                                            re.IGNORECASE)
    """Regular expression to match non-aarch64 architecture predefined
    macros."""
    COMPILER_MACROS_RE_PROG = re.compile(r'(?:\w*_|^)(%s)(?:_\w*|$)' %
                                         '|'.join(COMPILERS),
                                         re.IGNORECASE)
    """Regular expression to match compiler macros."""

    def __init__(self):
        self.in_aarch64 = []
        self.in_other_arch = []
        self.in_compiler = []
        self.if_lines = []
        self.in_comment = False

    def parse_line(self, line):
        """Parse preprocessor directives in a source line.

        Args:
            line (str): The line to parse.

        Returns:
            PreprocessorDirective: Information about the parsed directive. 
        """
        if line.lstrip().startswith('#'):
            return self._parse_directive_line(line)
        else:
            return PreprocessorDirective(directive_type=None)

    def _parse_directive_line(self, line):
        parts = line.lstrip().split(maxsplit=1)
        directive = parts[0][1:]
        if directive == 'error':
            return PreprocessorDirective(directive_type=PreprocessorDirective.TYPE_ERROR)
        elif directive == 'pragma':
            return PreprocessorDirective(directive_type=PreprocessorDirective.TYPE_PRAGMA)
        elif directive == 'if':
            expression = parts[1]
            self.in_aarch64.append(NaiveCpp._is_expression_aarch64(expression))
            self.in_other_arch.append(
                NaiveCpp._is_expression_non_aarch64(expression))
            is_compiler = NaiveCpp._is_expression_compiler(expression)
            self.in_compiler.append(is_compiler)
            self.if_lines.append(line)
            return PreprocessorDirective(directive_type=PreprocessorDirective.TYPE_CONDITIONAL, if_line=line,
                                         is_compiler=is_compiler)
        elif directive == 'elif':
            expression = parts[1]
            if self.in_aarch64:
                self.in_aarch64[-1] = \
                    NaiveCpp._is_expression_aarch64(expression)
            if self.in_other_arch:
                self.in_other_arch[-1] = \
                    NaiveCpp._is_expression_non_aarch64(expression)
            if self.in_compiler:
                is_compiler = NaiveCpp._is_expression_compiler(expression)
                self.in_compiler[-1] = \
                    is_compiler
            else:
                is_compiler = False
            return PreprocessorDirective(directive_type=PreprocessorDirective.TYPE_CONDITIONAL, if_line=line,
                                         is_compiler=is_compiler)
        elif directive == 'ifdef':
            macro = parts[1]
            self.in_aarch64.append(
                NaiveCpp.AARCH64_MACROS_RE_PROG.match(macro) is not None or None)
            self.in_other_arch.append(
                NaiveCpp.NON_AARCH64_MACROS_RE_PROG.match(macro) is not None or None)
            is_compiler = NaiveCpp.COMPILER_MACROS_RE_PROG.match(
                macro) is not None or None
            self.in_compiler.append(is_compiler)
            self.if_lines.append(line)
            return PreprocessorDirective(directive_type=PreprocessorDirective.TYPE_CONDITIONAL, if_line=line,
                                         is_compiler=is_compiler)
        elif directive == 'else':
            if self.in_aarch64:
                self.in_aarch64[-1] = \
                    NaiveCpp.tri_negate(
                        self.in_aarch64[-1])
            if self.in_other_arch:
                self.in_other_arch[-1] = \
                    NaiveCpp.tri_negate(
                        self.in_other_arch[-1])
            if self.in_compiler:
                self.in_compiler[-1] = \
                    NaiveCpp.tri_negate(
                        self.in_compiler[-1])
            if self.if_lines:
                if_line = self.if_lines[-1]
            else:
                if_line = line
            return PreprocessorDirective(directive_type=PreprocessorDirective.TYPE_CONDITIONAL, if_line=if_line)
        elif directive == 'endif':
            if self.in_aarch64:
                self.in_aarch64.pop()
            if self.in_other_arch:
                self.in_other_arch.pop()
            if self.in_compiler:
                self.in_compiler.pop()
            if self.if_lines:
                if_line = self.if_lines.pop()
            else:
                if_line = None
            return PreprocessorDirective(directive_type=PreprocessorDirective.TYPE_CONDITIONAL, if_line=if_line)
        else:
            return PreprocessorDirective(directive_type=PreprocessorDirective.TYPE_OTHER)

    @staticmethod
    def tri_negate(x):
        if x is None:
            return None
        else:
            return not x

    @staticmethod
    def _is_expression_x(expression, x):
        tokens = NaiveCpp.TOKEN_PROG.split(expression)
        for token in tokens:
            match = NaiveCpp.DEFINED_PROG.match(token)
            if not match:
                match = NaiveCpp.MACRO_PROG.match(token)
            if match:
                negated = match.group(1) == '!'
                macro = match.group(2)
                if x.match(macro) is not None:
                    return not negated
        return None

    @staticmethod
    def _is_expression_aarch64(expression):
        return NaiveCpp._is_expression_x(expression, NaiveCpp.AARCH64_MACROS_RE_PROG)

    @staticmethod
    def _is_expression_non_aarch64(expression):
        return NaiveCpp._is_expression_x(expression, NaiveCpp.NON_AARCH64_MACROS_RE_PROG)

    @staticmethod
    def _is_expression_compiler(expression):
        return NaiveCpp._is_expression_x(expression, NaiveCpp.COMPILER_MACROS_RE_PROG)

    @staticmethod
    def _in_x_code(x):
        for y in x:
            if y:
                return True
        return False

    def in_aarch64_specific_code(self):
        """Are we in aarch64 specific code?

        Returns:
            bool: True if we are currently in an #ifdef __aarch64_ or similar block, else False. 
        """
        return NaiveCpp._in_x_code(self.in_aarch64)

    def in_other_arch_specific_code(self):
        """Are we in other architecture (non-aarch64) specific code?

        Returns:
            bool: True if we are currently in an #ifdef OTHERARCH or similar block, else False. 
        """
        return NaiveCpp._in_x_code(self.in_other_arch)

    def in_compiler_specific_code(self):
        """Are we in compiler specific code?

        Returns:
            bool: True if we are currently in an #ifdef COMPILER or similar block, else False. 
        """
        return NaiveCpp._in_x_code(self.in_compiler)
