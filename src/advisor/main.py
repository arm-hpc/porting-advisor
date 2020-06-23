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

import advisor
from advisor.auto_scanner import AutoScanner
from advisor.html_report import HtmlReport
from advisor.issue_type_filter import IssueTypeFilter
from advisor.issue_types import ISSUE_TYPES
from advisor.localization import _
from advisor.report import Report
from advisor.scanners import Scanners
from progressbar import ProgressBar, UnknownLength
from progressbar.widgets import AnimatedMarker, Timer, Widget
import argparse
import os
import sys
import textwrap

def main():
    default_os = os.name
    if default_os == 'nt':
        default_os = 'windows'
    else:
        default_os = 'linux'

    epilog = _('Use:') + '\n' + \
        textwrap.fill(_('--issue-types=+CrossCompile to enable reporting of cross-compile specific issues.'),
                      initial_indent='  ',
                      subsequent_indent='    ') + '\n' + \
        textwrap.fill(_('--issue-types=+CompilerSpecific to enable reporting of use of compiler-specific macros.'),
                      initial_indent='  ',
                      subsequent_indent='    ') + '\n' + \
        textwrap.fill(_('--issue-types=+NoEquivalent to enable reporting of aarch64 ported code that does not use intrinsics inline assembly versus other architectures.'),
                      initial_indent='  ',
                      subsequent_indent='    ') + '\n\n' + \
        _('Available issue types:') + '\n' + \
        textwrap.fill(', '.join(sorted(ISSUE_TYPES.keys())),
                      initial_indent='  ',
                      subsequent_indent='  ')
    parser = argparse.ArgumentParser(
        prog=advisor.__project__,
        description=advisor.__summary__,
        epilog=epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('root', metavar='DIRECTORY',
                        help=_('root directory of source tree (default: .)'),
                        default='.')
    parser.add_argument('--issue-types',
                        help=_('modify the types of issue that are reported (default: %s)') % IssueTypeFilter.DEFAULT_FILTER)
    parser.add_argument('--no-progress', action='store_false',
                        help=("don't show progress bar"),
                        dest='progress')
    parser.add_argument('--output',
                        help=_('output file name'),
                        default=None)
    parser.add_argument('--quiet', action='store_true',
                        help=_('suppress file errors'),
                        default=False)
    parser.add_argument('--json', action='store_true',
                        help=_('output verbose results as json'),
                        default=False)
    parser.add_argument('--avx',
                        help=_('output file name in csv format for avx instruction'),
                        default=None)
    parser.add_argument('--target-os',
                        help=_('target operating system: all,linux,windows (default: %s)') % default_os,
                        default=default_os)
    parser.add_argument('--version', action='version',
                        version='%(prog)s ' + advisor.__version__)

    args = parser.parse_args()

    if not os.path.exists(args.root):
        print(_('%s: directory not found.') % args.root, file=sys.stderr)
        sys.exit(1)
    elif not os.path.isdir(args.root):
        print(_('%s: not a directory.') % args.root, file=sys.stderr)
        sys.exit(1)

    if not args.output:
        report = Report(args.root, report_errors=not args.quiet, target_os=args.target_os)
    else:
        report = HtmlReport(args.root, report_errors=not args.quiet, target_os=args.target_os)

    scanners = Scanners(args.issue_types)
    scanners.initialize_report(report)

    scanner = AutoScanner(scanners)
    if args.progress:
        class FileNameLabel(Widget):
            def __init__(self):
                self.fname = None

            def set_file_name(self, fname):
                self.fname = fname

            def update(self, pbar):
                return self.fname if self.fname else ''

        def progress_callback(filename):
            fname_label.set_file_name(filename)
            progress.update()

        fname_label = FileNameLabel()
        progress = ProgressBar(maxval=UnknownLength,
                               widgets=[AnimatedMarker(), ' ', Timer(), ' ', fname_label],
                               poll=0.1)
        progress.start()
    scanner.scan_tree(args.root, report,
                      progress_callback=progress_callback if args.progress else None)
    if args.progress:
        fname_label.set_file_name(None)
        progress.finish()

    scanners.finalize_report(report)

    if args.output:
        with open(args.output, 'w') as f:
            if args.json:
                report.write_json(f, args.issue_types)
            else:
                report.write(f)
    elif args.json:
            report.write_json(sys.stdout, args.issue_types)
    else:
        if args.avx:
            report.write_csv(args.avx)
        else:
            report.write(sys.stdout)
            print('\nUse --output FILENAME.html to generate an HTML report or --avx FILENAME.csv to generate csv file.')

if __name__ == '__main__':
    main()
