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

import os

from .files_scanned_remark import FilesScannedRemark
from .no_issues_found_remark import NoIssuesFoundRemark
from .report_item import ReportItem
import json
import csv


class Report:
    def __init__(self, root_directory, report_errors=True, target_os='linux'):
        self.issues = []
        self.errors = []
        self.remarks = []
        self.report_errors = report_errors
        self.root_directory = root_directory
        self.source_files = []
        self.source_dirs = set()
        self.target_os = target_os
        self.filename_data = ['FILENAME',]
        self.avx256_data = ['NUM_OF_AVX256_INST',]
        self.avx512_data = ['NUM_OF_AVX512_INST',]
        self.total_data = ['TOTAL_AVX_INST',]

    def add_source_file(self, source_file):
        self.source_files.append(source_file)
        self.source_dirs.add(os.path.dirname(source_file))

    def add_issue(self, item):
        self.issues.append(item)

    def add_remark(self, item):
        self.remarks.append(item)

    def add_error(self, error):
        self.errors.append(error)

    def write(self, output_file):
        items = {}
        for item_type in ReportItem.TYPES:
            items[item_type] = []
        all_items = self.remarks + self.issues
        if self.report_errors:
            all_items += self.errors
        for item in all_items:
            items[item.item_type].append(item)
        items[ReportItem.SUMMARY].append(
            FilesScannedRemark(len(self.source_files)))
        if not items[ReportItem.NEGATIVE] and not items[ReportItem.NEUTRAL]:
            items[ReportItem.POSITIVE].append(NoIssuesFoundRemark())
        sorted_items = []
        for item_type in ReportItem.TYPES:
            sorted_items += sorted(items[item_type], key=lambda item: (
                (item.filename if item.filename else '') + ':' + item.description))
        self.write_items(output_file, sorted_items)

    def write_json(self, output_file, issue_types):
        self.issue_types = issue_types
        # munge 'self' fields so it can be serialized
        self.source_dirs = list(self.source_dirs)
        self.issues = [i.__class__.__name__ + ': ' + str(i) for i in self.issues]
        self.errors = [i.__class__.__name__ + ': ' + str(i) for i in self.errors]
        self.remarks = [i.__class__.__name__ + ': ' + str(i) for i in self.remarks]
        print(json.dumps(self.__dict__, sort_keys=True, indent=4), file=output_file)

    """This will generate CSV file for avx insturction"""
    def write_csv(self, csvfilename):
        with open(csvfilename, "w") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.filename_data)
            writer.writeheader()
            writer = csv.DictWriter(csvfile, fieldnames=self.avx256_data)
            writer.writeheader()
            writer = csv.DictWriter(csvfile, fieldnames=self.avx512_data)
            writer.writeheader()
            writer = csv.DictWriter(csvfile, fieldnames=self.total_data)
            writer.writeheader()

    def write_items(self, output_file, items):
        for item in items:
            print(item, file=output_file)
