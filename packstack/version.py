# -*- coding: utf-8 -*-

import os
import pkg_resources

from .installer.utils import execute


VERSION = ['2014', '2']
OS_RELEASE = 'Juno'
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
    return '{0}.dev{1}.{2}'.format(
        '.'.join(VERSION),
        snap_tag.strip(),
        git_hash.strip(),
    )


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
