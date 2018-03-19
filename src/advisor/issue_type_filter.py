"""
Copyright 2017-2018 Arm Ltd.

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
from .scanner import Scanner

class IssueTypeFilter(Scanner):
    """Filters issues by type."""

    DEFAULT_FILTER = '-CompilerSpecific,-CrossCompile,-NoEquivalent'
    """Default issue filter. This is always prepended to the filter supplied
    on the command line."""

    def __init__(self, config_string):
        """Filters issues by type.

        Args:
            config_str (str): The filter configuration string.
            This is a comma-separated list of issue types to report. Alternatively
            the configuration string may be used to add or remove issues from the
            default filter. In this case issue types prefixed with '-' are removed
            by the filter. Issue types prefixed with '+' are included by the filter.
        """
        if config_string and not config_string.startswith('+') and not config_string.startswith('-'):
            # User wants to replace the default list.
            pass
        elif config_string:
            config_string = IssueTypeFilter.DEFAULT_FILTER + ',' + config_string
        else:
            config_string = IssueTypeFilter.DEFAULT_FILTER

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

    def finalize_report(self, report):
        filtered_issues = list()
        for issue in report.issues:
            want_this_issue = True
            for (klass, want_this_issue_type) in self.klasses:
                if isinstance(issue, klass):
                    want_this_issue = want_this_issue_type
            if want_this_issue:
                filtered_issues.append(issue)
        report.issues = filtered_issues
