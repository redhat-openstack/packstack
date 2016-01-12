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

import os
import pkg_resources

from .installer.utils import execute


VERSION = ['8', '0', '0']
OS_RELEASE = 'Mitaka'
RESERVE_STR = None


def vr_from_git():
    """Returns VR string calculated from GIT repo."""
    proj_dir = os.path.dirname(os.path.dirname(__file__))
    rc, tag = execute(
        'git describe --exact-match',
        workdir=proj_dir,
        use_shell=True,
        can_fail=False,
        log=False
    )
    if not rc:
        # we are on tagged commit, so let's use the tag as VR string
        return tag.strip()

    rc, description = execute(
        'git describe --always',
        workdir=proj_dir,
        use_shell=True,
        log=False
    )
    if '-' in description:
        # last tag has been found
        tag, snap_tag, git_hash = description.split('-')
    else:
        # no tag has been found
        tag = '.'.join(VERSION)
        rc, git_hash = execute(
            'git log -n1 --pretty=format:%h',
            workdir=proj_dir,
            use_shell=True,
            log=False
        )
        git_hash = 'g{0}'.format(git_hash)
        rc, snap_tag = execute(
            'git log --oneline | wc -l',
            workdir=proj_dir,
            use_shell=True,
            log=False
        )

    tag, snap_tag, git_hash = tag.strip(), snap_tag.strip(), git_hash.strip()
    return '{tag}.dev{snap_tag}.{git_hash}'.format(**locals())


def vr_from_setuptools():
    """Returns VR string fetched from setuptools."""
    requirement = pkg_resources.Requirement.parse('packstack')
    provider = pkg_resources.get_provider(requirement)
    return provider.version


def release_string():
    return OS_RELEASE


def version_string():
    try:
        version = vr_from_git()
    except Exception:
        # Not a git repo, so get version from setuptools
        try:
            version = vr_from_setuptools()
        except Exception:
            # In case of problem with setuptools, return version
            # saved by release.sh or VERSION if nothing was saved
            version = RESERVE_STR if RESERVE_STR else '.'.join(VERSION)
    return version
