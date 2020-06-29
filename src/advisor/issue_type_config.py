"""
Copyright 2017-2020 Arm Ltd.

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

import sys


from .issue_types import ISSUE_TYPES
from .report_item import ReportItem

class IssueTypeConfig:
    """Issue type filter configuration"""

    DEFAULT_FILTER = '-CompilerSpecific,-CrossCompile,-NoEquivalent'
    """Default issue filter. This is always prepended to the filter supplied
    on the command line."""

    def __init__(self, config_string=None):
        """Parse the --issue-types command line argument to get the issue type
        filter configuration.

        Args:
            config_str (str): The filter configuration string.
            This is a comma-separated list of issue types to report. Alternatively
            the configuration string may be used to add or remove issues from the
            default filter. In this case issue types prefixed with '-' are removed
            by the filter. Issue types prefixed with '+' are included by the filter.
        """
        if config_string and not config_string.startswith('+') and not config_string.startswith('-'):
            # User wants to replace the default list.
            self.default_include = False
            print('yes')
        elif config_string:
            config_string = IssueTypeConfig.DEFAULT_FILTER + ',' + config_string
            self.default_include = True
        else:
            config_string = IssueTypeConfig.DEFAULT_FILTER
            self.default_include = True

        issue_types = config_string.split(',')
        self.klasses = []
        for issue_type in issue_types:
            if not issue_type:
                continue

            if issue_type.startswith('-'):
                want_this_issue_type = False
                issue_type = issue_type[1:]
            elif issue_type.startswith('+'):
                want_this_issue_type = True
                issue_type = issue_type[1:]
            else:
                want_this_issue_type = True

            try:
                klass = ISSUE_TYPES[issue_type]
                self.klasses.append((klass, want_this_issue_type))
            except KeyError:
                print('Issue type filter: unknown issue type: %s' % issue_type, file=sys.stderr)

    def filter_issue_types(self, issue_types):
        """Filters the given dictionary of issue types.

        This function is careful to preserve the order of issue types given on
        the command line if the user passed an explicit list.
        """

        sorted_issue_types = [cls for _, cls in sorted(issue_types.items(), key=lambda name_cls: name_cls[0])]
        if not self.default_include:
            # Preserve the order of issue types given on the command line.
            source_list = []
            for (cls, _) in self.klasses:
                for issue_type in sorted_issue_types:
                    if (issue_type == cls or issubclass(issue_type, cls)) and not issue_type in source_list:
                        source_list.append(issue_type)
        else:
            source_list = sorted_issue_types
        ret = []
        for klass_a in source_list:
            want_this_class = self.default_include
            for (klass_b, want_this_issue_type) in self.klasses:
                if klass_a == klass_b or issubclass(klass_a, klass_b):
                    want_this_class = want_this_issue_type
            if want_this_class:
                ret.append(klass_a)
        return ret

    def include_issue_p(self, issue):
        """Return whether this issue is wanted or not according to the issue type
        filter configuration."""
        want_this_issue = self.default_include
        for (klass, want_this_issue_type) in self.klasses:
            if isinstance(issue, klass):
                want_this_issue = want_this_issue_type
        return want_this_issue