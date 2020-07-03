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
import csv
import os
import tempfile
import unittest

class TestAvsCsvReport(unittest.TestCase):
    def test_avx_csv_report(self):
        with tempfile.NamedTemporaryFile() as output,\
             tempfile.TemporaryDirectory() as srcdir:
            self._populate_source_directory(srcdir)
            argv = ['--output', output.name,
                    '--output-format', 'csv_issue_type_count_by_file',
                    '--issue-types', 'Avx256Intrinsic,Avx512Intrinsic',
                    srcdir]
            advisor.main.main(argv)
            expected_files_seen=set(['file.c', 'file256.c', 'file512.c', 'file_with_port.c'])
            actual_files_seen=set()
            expected_intrinsics_per_file={
                'file.c':
                    { 'Avx256Intrinsic': 0,
                      'Avx512Intrinsic': 0 },
                'file256.c':
                    { 'Avx256Intrinsic': 2,
                      'Avx512Intrinsic': 0 },
                'file512.c':
                    { 'Avx256Intrinsic': 0,
                      'Avx512Intrinsic': 2 },
                'file_with_port.c':
                    { 'Avx256Intrinsic': 0,
                      'Avx512Intrinsic': 0 }
                }
            with open(output.name) as csvf:
                csv_reader = csv.DictReader(csvf)
                for row in csv_reader:
                    filename = os.path.basename(row['filename'])
                    actual_files_seen.add(filename)
                    expected_intrinsics=expected_intrinsics_per_file[filename]
                    for (intrinsic_type, expected_count) in expected_intrinsics.items():
                        self.assertEquals(int(row[intrinsic_type]), expected_count)
            self.assertEquals(expected_files_seen, actual_files_seen)

    def test_avx_csv_report_no_filter(self):
        with tempfile.NamedTemporaryFile() as output,\
             tempfile.TemporaryDirectory() as srcdir:
            self._populate_source_directory(srcdir)
            argv = ['--output', output.name,
                    '--output-format', 'csv_issue_type_count_by_file',
                    '--issue-types', 'Avx256Intrinsic,Avx512Intrinsic',
                    '--no-filter',
                    srcdir]
            advisor.main.main(argv)
            expected_files_seen=set(['file.c', 'file256.c', 'file512.c', 'file_with_port.c'])
            actual_files_seen=set()
            expected_intrinsics_per_file={
                'file.c':
                    { 'Avx256Intrinsic': 0,
                      'Avx512Intrinsic': 0 },
                'file256.c':
                    { 'Avx256Intrinsic': 2,
                      'Avx512Intrinsic': 0 },
                'file512.c':
                    { 'Avx256Intrinsic': 0,
                      'Avx512Intrinsic': 2 },
                'file_with_port.c':
                    { 'Avx256Intrinsic': 1,
                      'Avx512Intrinsic': 0 }
                }
            with open(output.name) as csvf:
                csv_reader = csv.DictReader(csvf)
                for row in csv_reader:
                    filename = os.path.basename(row['filename'])
                    actual_files_seen.add(filename)
                    expected_intrinsics=expected_intrinsics_per_file[filename]
                    for (intrinsic_type, expected_count) in expected_intrinsics.items():
                        self.assertEquals(int(row[intrinsic_type]), expected_count)
            self.assertEquals(expected_files_seen, actual_files_seen)

    def _populate_source_directory(self, srcdir):
        def write_file_contents(srcdir, fname, contents):
            with open(os.path.join(srcdir, fname), 'w') as f:
                f.write(contents)

        write_file_contents(srcdir, 'file.c', '''
#include "yyy.h"

void abc() {
    printf("hello, world!\n");
}
''')
        write_file_contents(srcdir, 'file256.c', '''
__m256d foo(__m256d a, __m256d b) {
    __m256d c = _mm256_add_pd(a, b);
    return c;
}

__m128d bar(__m256d a) {
    return _mm256_extractf128_pd(a, 1); 
}
''')
        write_file_contents(srcdir, 'file512.c', '''
#include "zzz.h"

__m512d foo(__m512d a, __m512d b) {
    __m512d c = _mm512_add_pd(a, b);
    return c;
}

__m128d bar(__m256d a) {
    return _mm512_extractf64x2_pd(a, 1); 
}
''')
        write_file_contents(srcdir, 'file_with_port.c', '''


// a comment

#if defined(__x86_64__)
__m256d foo(__m256d a, __m256d b) {
    __m256d c = _mm256_add_pd(a, b);
    return c;
}
#elif defined(__aarch64__)
svfloat64x4_t foo(svfloat64x4_t a, svfloat64x4_t b) {
    svfloat64x4_t c = svadd[_f64]_z(pg, a, b);
    return c;
}
#else
#endif
''')
