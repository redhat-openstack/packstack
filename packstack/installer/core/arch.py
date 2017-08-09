# -*- coding: utf-8 -*-
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Simple routines to map host architectures as expected by various components.
"""

import os


def kernel_arch():
    """Return the kernel arch."""
    return os.uname()[4]


def dib_arch():
    """Return the kernel arch or the more appropriate DiB arch."""
    DIB_MAP = {
        'x86_64': 'amd64',
        'aarch64': 'arm64',
    }
    return DIB_MAP.get(kernel_arch(), kernel_arch())


def cirros_arch():
    """Return the kernel arch or the more appropriate cirros arch."""
    CIRROS_MAP = {
        'ppc64le': 'powerpc',
        'aarch64': 'arm',
    }
    return CIRROS_MAP.get(kernel_arch(), kernel_arch())
