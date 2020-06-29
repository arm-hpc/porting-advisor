"""
Copyright 2020 Arm Ltd.

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

from .csv_report import CsvReport
from .csv_issue_type_count_by_file_report import CsvIssueTypeCountByFileReport
from .html_report import HtmlReport
from .json_report import JsonReport
from .text_report import Report
from enum import Enum

class ReportOutputFormat(Enum):
    AUTO = 'auto'
    CSV_ISSUE_TYPE_COUNT_BY_FILE = 'csv_issue_type_count_by_file'
    CSV = 'csv'
    JSON = 'json'
    HTML = 'html'
    TEXT = 'text'
    DEFAULT = AUTO

class ReportFactory:
    """ Factory class for report output formats. """

    def createReport(self, root_directory, target_os='linux', issue_type_config=None, output_format=ReportOutputFormat.TEXT):
        if output_format == ReportOutputFormat.TEXT:
            report = Report(root_directory, target_os=target_os)
        elif output_format == ReportOutputFormat.HTML:
            report = HtmlReport(root_directory, target_os=target_os)
        elif output_format == ReportOutputFormat.CSV:
            report = CsvReport(root_directory, target_os=target_os)
        elif output_format == ReportOutputFormat.CSV_ISSUE_TYPE_COUNT_BY_FILE:
            report = CsvIssueTypeCountByFileReport(root_directory, target_os=target_os, issue_type_config=issue_type_config)
        elif output_format == ReportOutputFormat.JSON:
            report = JsonReport(root_directory, target_os=target_os)
        else:
            raise ValueError(output_format)
        return report
