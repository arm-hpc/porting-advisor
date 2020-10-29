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

import advisor.main
from advisor.issue_type_config import IssueTypeConfig
import json
import os
import tempfile
import unittest

class TestJsonReportFromCommandLine(unittest.TestCase):
    def test_json_report_from_command_line(self):
        with tempfile.NamedTemporaryFile() as output,\
             tempfile.TemporaryDirectory() as srcdir:
            self._populate_source_directory(srcdir)
            argv = ['--output', output.name,
                    '--output-format', 'json',
                    srcdir]
            advisor.main.main(argv)

            with open(output.name) as jsonf:
                json_top = json.load(jsonf)

            self.assertIn('errors', json_top)
            self.assertEqual(len(json_top['errors']), 0)
            self.assertIn('issues', json_top)
            self.assertEqual(len(json_top['issues']), 2)
            self.assertIn('remarks', json_top)
            self.assertEqual(len(json_top['remarks']), 1)
            self.assertIn('issue_types', json_top)
            self.assertEqual(json_top['issue_types'], IssueTypeConfig.DEFAULT_FILTER)
            self.assertIn('target_os', json_top)
            self.assertIn(json_top['target_os'], ['linux', 'windows'])
            self.assertIn('root_directory', json_top)
            self.assertEqual(json_top['root_directory'], srcdir)
            self.assertIn('source_dirs', json_top)
            self.assertEqual(len(json_top['source_dirs']), 1)
            self.assertEqual(json_top['source_dirs'][0], srcdir)
            self.assertIn('source_files', json_top)
            self.assertEqual(len(json_top['source_files']), 3)
            seen_test_negative = False
            seen_test_neutral = False
            seen_config_guess = False
            for fname in json_top['source_files']:
                if 'test_negative.c' in fname:
                    seen_test_negative = True
                elif 'test_neutral.c' in fname:
                    seen_test_neutral = True
                elif 'config.guess' in fname:
                    seen_config_guess = True
                else:
                  self.fail('Unexpected source file name in JSON output')
            self.assertTrue(seen_test_negative)
            self.assertTrue(seen_test_neutral)
            self.assertTrue(seen_config_guess)
            seen_issue1 = False
            seen_issue2 = False
            for issue in json_top['issues']:
                if 'test_negative.c' in issue:
                    self.assertIn('InlineAsm', issue)
                    seen_issue1 = True
                elif 'test_neutral.c' in issue:
                    self.assertIn('PragmaSimd', issue)
                    seen_issue2 = True
                else:
                    self.fail('Unexpected issue in JSON output')
            self.assertTrue(seen_issue1)
            self.assertTrue(seen_issue2)
            seen_config_guess = False
            for remark in json_top['remarks']:
                if 'config.guess' in remark:
                    seen_config_guess = True
            self.assertTrue(seen_config_guess)

    def _populate_source_directory(self, srcdir):
        def write_file_contents(srcdir, fname, contents):
            with open(os.path.join(srcdir, fname), 'w') as f:
                f.write(contents)

        write_file_contents(srcdir, 'test_negative.c', '''
__asm__("mov r0, r1")
''')
        write_file_contents(srcdir, 'test_neutral.c', '''
#pragma simd foo
''')
        write_file_contents(srcdir, 'config.guess', '''
'aarch64:Linux'
''')
