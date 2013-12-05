# -*- coding: utf-8 -*-

"""
This module provides all the predefined variables.
"""

import os
import pwd
import sys
import datetime
import tempfile
import random
import string
import errno
import logging

from .utils import get_current_user

# Iinitializes the directory by creating it or
# changing ownsership it already exists.
# in case there's a problem it falls back to the
# default directory
# returns the name of the created directory
def init_directory(dirname, force_ownership=True):
    try:
        os.makedirs(dirname, 0700)
    except OSError as e:
        if e.errno == errno.EEXIST and os.path.isdir(dirname):
            # directory is already created, check ownership
            stat = os.stat(dirname)
            if (force_ownership and stat.st_uid == 0 and
                os.getuid() != stat.st_uid):
                print ('%s is already created and owned by root. Please change '
                       'ownership and try again.' % dirname)
                sys.exit(1)
        elif e.errno == errno.EACCES:
            logging.info("Can't create directory %s." % dirname)
            return None
        else:
            raise
    finally:
        uid, gid = get_current_user()
        if uid != 0 and os.getuid() == 0:
            try:
                os.chown(dirname, uid, gid)
            except Exception, ex:
                if force_ownership:
                    print ('Unable to change owner of %s. Please fix ownership'
                           ' manually and try again.' % dirname)
                    sys.exit(1)
    return dirname

APP_NAME = "Installer"

FILE_YUM_VERSION_LOCK = "/etc/yum/pluginconf.d/versionlock.list"

PACKSTACK_VAR_DIR = init_directory("/var/tmp/packstack")
PACKSTACK_LOG_DIR = init_directory("/var/log/packstack", force_ownership=False)
if not PACKSTACK_LOG_DIR:
    PACKSTACK_LOG_DIR = PACKSTACK_VAR_DIR

_tmpdirprefix = datetime.datetime.now().strftime('%Y%m%d-%H%M%S-')
LOG_DIR = ""
VAR_DIR = tempfile.mkdtemp(prefix=_tmpdirprefix, dir=PACKSTACK_VAR_DIR,)
if PACKSTACK_VAR_DIR != PACKSTACK_LOG_DIR:
    LOG_DIR = VAR_DIR.replace("tmp", "log")
    init_directory(LOG_DIR)
else:
    LOG_DIR = VAR_DIR


PUPPET_MANIFEST_RELATIVE = "manifests"
PUPPET_MANIFEST_DIR = os.path.join(VAR_DIR, PUPPET_MANIFEST_RELATIVE)

FILE_INSTALLER_LOG = "setup.log"

DIR_PROJECT_DIR = os.environ.get('INSTALLER_PROJECT_DIR', os.path.join(os.getcwd(), 'packstack'))
DIR_PLUGINS = os.path.join(DIR_PROJECT_DIR, "plugins")
DIR_MODULES = os.path.join(DIR_PROJECT_DIR, "modules")



EXEC_RPM = "rpm"
EXEC_SEMANAGE = "semanage"
EXEC_NSLOOKUP = "nslookup"
EXEC_CHKCONFIG = "chkconfig"
EXEC_SERVICE = "service"
EXEC_IP = "ip"

# space len size for color print
SPACE_LEN = 70
