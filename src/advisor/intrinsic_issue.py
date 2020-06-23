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

from .localization import _
from .report_item import ReportItem


class IntrinsicIssue(ReportItem):
    def __init__(self, filename, lineno, intrinsic, function=None):
        description = _("architecture-specific intrinsic: %s") % intrinsic
        super().__init__(description=description, filename=filename,
                         lineno=lineno, item_type=ReportItem.NEGATIVE,
                         function=function)

"""Class for AVX256 intrinsic issues"""
class AVX256IntrinsicIssue(ReportItem):
    def __init__(self, filename, lineno, intrinsic, function=None):
        description = _("architecture-specific AVX256 intrinsic: %s") % intrinsic
        super().__init__(description=description, filename=filename,
                         lineno=lineno, item_type=ReportItem.NEGATIVE,
                         function=function)

"""Class for AVX512 intrinsic issues"""
class AVX512IntrinsicIssue(ReportItem):
    def __init__(self, filename, lineno, intrinsic, function=None):
        description = _("architecture-specific AVX512 intrinsic: %s") % intrinsic
        super().__init__(description=description, filename=filename,
                         lineno=lineno, item_type=ReportItem.NEGATIVE,
                         function=function)
