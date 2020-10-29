1.4.1 2020-10-29

  * Fix for https://github.com/arm-hpc/porting-advisor/issues/5.

1.4 2020-07-03

  * Add `--output-format` command line argument to specify the output format.
  * Add automatic detection of output format from output file name.
  * Add CSV output format.
  * Add `--no-filter` command line argument to prevent filtering of
    architecture-specific code that looks like it already has an aarch64
    equivalent.
  * Distinguish AVX-256 and AVX-512 intrinsics from other intrinsics.
  * Fix issue where not all issue types showed up in `--help` output.

1.3 2019-01-25

  * Count the number of inline assembly or intrinsics with aarch64 equivalents
    more reliably.
  * Fix parsing of function definitions with a return type split across multiple
    lines.
  * Extend the function parsing to support C++ method definitions.
  * Include the issue / remark type in the JSON output.

1.2 2018-04-20

  * Add x64 to non-aarch64 architecture strings.
  * Add detection of two cross-compile specific issues.
  * Add function / macro name to source file issues.
  * Add issue type filter command line option.
  * Add `--target-os` command line option.
  * Add progress bar during scanning.
  * Detect hard-coded architecture defines in `Makefile`s (e.g. `-DOTHERARCH`).
  * Detect use of old Visual C++ runtime (Windows on Arm specific).
  * Detect functions that use intrinsics or inline assembly on other
    architectures, but not on Arm.
  * Do not report `_fxstat` as an intrinsic.
  * Fix an exception caused by malformed preprocessor directives.
  * Ignore charset decoding errors in source files.
  * Ignore source file issues in comments.
  * Scan macro bodies for intrinsics and inline assembly.

1.1 2018-02-21

  * Fix error message when source tree root directory not found.
  * Add missing preprocessor support for `#ifndef`.
  * Report negative items before neutral items.
  * Ignore version control blobs.
  * Fix condition for reporting `#error` to ignore non-architecture specific macros.
  * Include the base name of the source tree root directory in the header of the HTML report.
  * Fix missing icons in the HTML report.

1.0 2017-12-21

  * Initial release.
