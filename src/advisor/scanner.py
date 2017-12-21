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
import sys
import traceback
from .error import Error


class Scanner:
    def accepts_file(self, filename):
        """Overriden by subclasses to decide whether or not to accept a
        file.

        Args:
            filename (str): Filename under consideration.

        Returns:
            bool: True if the file with the given name is accepted by this
            scanner, else False.
        """
        return False

    def finalize_report(self, report):
        """Finalizes the report for this scanner.

        Args:
            report (Report): Report to finalize_report.
        """
        pass

    def has_scan_file_object(self):
        return hasattr(self, 'scan_file_object')

    def initialize_report(self, report):
        """Initialises the report for this scanner, which may include
        initializing scanner-specific fields in the Report.

        Args:
            report (Report): Report to initialize_report.
        """
        pass

    def scan_file(self, filename, report):
        """Scans the file with the given name for potential porting issues.

        Args:
            filename (str): Name of the file to scan.
            report (Report): Report to add issues to.
        """
        try:
            report.add_source_file(filename)
            self.scan_filename(filename, report)
            if self.has_scan_file_object():
                with open(filename) as f:
                    try:
                        self.scan_file_object(filename, f, report)
                    except KeyboardInterrupt:
                        raise
                    except:
                        report.add_error(Error(description=str(traceback.format_exception(*sys.exc_info())[-1].strip()),
                                               filename=filename))
        except KeyboardInterrupt:
            raise
        except:
            report.add_error(Error(description=str(traceback.format_exc()),
                                   filename=filename))

    def scan_filename(self, filename, report):
        """Overridden by subclasses to scan for potential porting issues based
        on the name of the file.

        Args:
            filename (str): Name of the file to scan.
            report (Report): Report to add issues to.
        """
        pass

    def scan_tree(self, root, report):
        """Scans the filesysem tree starting at root for potential porting issues.

        Args:
            root (str): The root of the filesystem tree to scan.
            report (Report): Report to add issues to.
        """
        for dirName, _, fileList in os.walk(root):
            for fname in fileList:
                path = os.path.join(dirName, fname)
                self.scan_file(path, report)
