aarch64 Porting Advisor
=======================

This tool scans for potential unported or non-portable code in source code
trees.

The following types of issue are reported by default:
* Inline assembly with no corresponding aarch64 inlne assembly.
* Asssembly source files with no corresponding aarch64 assembly source files.
* Missing aarch64 architecture detection in autoconf config.guess scripts.
* Linking against libraries that are not available on the aarch64 architecture.
* Use of architecture specific intrinsics.
* Preprocessor errors that trigger when compiling on aarch64.
* Use of old Visual C++ runtime (Windows specific).

The following types of issues are detected, but not reported by default:
* Compiler specific code guarded by compiler specific pre-defined macros.

The following types of cross-compile specific issues are detected, but not
reported by default.
* Architecture detection that depends on the host rather than the target.
* Use of build artifacts in the build process.

Install
-------

python3 setup.py install

Usage
-----

```
usage: porting-advisor [-h] [--issue-types ISSUE_TYPES] [--no-progress]
                       [--output OUTPUT] [--quiet] [--target-os TARGET_OS]
                       [--version]
                       DIRECTORY

Produces an aarch64 porting readiness report.

positional arguments:
  DIRECTORY             root directory of source tree (default: .)

optional arguments:
  -h, --help            show this help message and exit
  --issue-types ISSUE_TYPES
                        modify the types of issue that are reported (default:
                        -CompilerSpecific,-CrossCompile,-NoEquivalent)
  --no-progress         don't show progress bar
  --output OUTPUT       output file name
  --quiet               suppress file errors
  --target-os TARGET_OS
                        target operating system: all,linux,windows (default:
                        linux)
  --version             show program's version number and exit

Use:
  --issue-types=+CrossCompile to enable reporting of cross-compile
    specific issues.
  --issue-types=+CompilerSpecific to enable reporting of use of
    compiler-specific macros.
  --issue-types=+NoEquivalent to enable reporting of aarch64 ported
    code that does not use intrinsics inline assembly versus other
    architectures.

Available issue types:
  ArchSpecificLibrary, AsmSource, CompilerSpecific, ConfigGuess,
  CrossCompile, DefineOtherArch, InlineAsm, Intrinsic, NoEquivalent,
  OldCrt, PragmaSimd, PreprocessorError
```

Caveats
-------

This tool scans all files in a source tree, regardless of whether they are
included by the build system or not. As such it may erroneously report issues in
files that appear in the source tree but are excluded by the build system.

License
-------

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
