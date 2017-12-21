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

INTRINSICS = [r'_mm(?:[0-9]+)?_\w+',
              r'_addcary\w+',
              r'_allow_cpu_features',
              r'_andn_\w+',
              r'_addcarry\w+',
              r'_bext\w+',
              r'_bit_scan_\w+',
              r'_BitScan\w+',
              r'_bittest\w+',
              r'_bls\w+',
              r'_bnd_\w+',
              r'_bswap\w+',
              r'_bzhi\w+',
              r'_cast[uf]\w+',
              r'_cvt\w+',
              r'_fx\w+',
              r'_invpcid',
              r'_loadbe_\w+',
              r'_lrot\w+',
              r'_lzcnt\w',
              r'_pdep_\w+',
              r'_pext_\w+',
              r'_popcnt\w+',
              r'_rdpip_\w+',
              r'_rdpmc',
              r'_rdrand\w+',
              r'_rdtsc',
              r'__rdtscp',
              r'_readfsbase_\w+',
              r'_readgsbase_\w+',
              r'_rotl\w*',
              r'_rotr\w*',
              r'_rotw\w',
              r'_storebe\w+',
              r'_subborrow\w+',
              r'_tzcnt\w+',
              r'_writefsbase_\w+',
              r'_writegsbase_\w+',
              r'_xabort',
              r'_xbegin',
              r'_xend',
              r'_xgetbv',
              r'_xrstor\w+',
              r'_xsave\w+',
              r'_xsetbv',
              r'_xtest',
              r'__builtin_ia32_\w+',
              r'vec_v\w+',
              r'_otherarch_intrinsic_\w+']
"""List of architecture-specific intrinsics."""
