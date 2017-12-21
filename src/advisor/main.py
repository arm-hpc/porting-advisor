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

import advisor
from advisor.auto_scanner import AutoScanner
from advisor.html_report import HtmlReport
from advisor.localization import _
from advisor.report import Report
from advisor.scanners import Scanners
import argparse
import os
import sys


def main():
    parser = argparse.ArgumentParser(
        prog=advisor.__project__,
        description=advisor.__summary__)
    parser.add_argument('root', metavar='DIRECTORY',
                        help=_('root directory of source tree (default: .)'),
                        default='.')
    parser.add_argument('--output',
                        help=_('output file name'),
                        default=None)
    parser.add_argument('--quiet', action='store_true',
                        help=_('suppress file errors'),
                        default=False)
    parser.add_argument('--version', action='version',
                        version='%(prog)s ' + advisor.__version__)

    args = parser.parse_args()

    if not os.path.exists(args.root):
        print(_('%s: directory not found.') % args.output, file=sys.stderr)
        sys.exit(1)
    elif not os.path.isdir(args.root):
        print(_('%s: not a directory.') % args.output, file=sys.stderr)
        sys.exit(1)

    if not args.output:
        report = Report(args.root, report_errors=not args.quiet)
    else:
        report = HtmlReport(args.root, report_errors=not args.quiet)

    scanners = Scanners()
    scanners.initialize_report(report)

    scanner = AutoScanner(scanners)
    scanner.scan_tree(args.root, report)

    scanners.finalize_report(report)

    if args.output:
        with open(args.output, 'w') as f:
            report.write(f)
    else:
        report.write(sys.stdout)
        print('\nUse --output FILENAME.html to generate an HTML report.')


if __name__ == '__main__':
    main()
