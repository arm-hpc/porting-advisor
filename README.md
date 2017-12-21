aarch64 Porting Advisor
=======================

This tool scans for potential unported or non-portable code in source code
trees.

The following types of issue are reported:
* Inline assembly with no corresponding aarch64 inlne assembly.
* Asssembly source files with no corresponding aarch64 assembly source files.
* Missing aarch64 architecture detection in autoconf config.guess scripts.
* Linking against libraries that are not available on the aarch64 architecture.
* Compiler specific code guarded by compiler specific pre-defined macros.
* Use of architecture specific intrinsics.
* Preprocessor errors that trigger when compiling on aarch64.

Install
-------

python3 setup.py install

Usage
-----

 usage: porting-advisor [-h] [--output OUTPUT] [--quiet] [--version] DIRECTORY
 
 Produces an aarch64 porting readiness report.
 
 positional arguments:
   DIRECTORY        root directory of source tree (default: .)
 
 optional arguments:
   -h, --help       show this help message and exit
   --output OUTPUT  output file name
   --quiet          suppress file errors
   --version        show program's version number and exit

Caveats
-------

This tool scans all files in a source tree, regardless of whether they are
included by the build system or not. As such it may erroneously report issues in
files that appear in the source tree but are excluded by the build system.

License
-------

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
