# -*- coding: utf-8 -*-

import re
import types
import logging
import subprocess

from ..exceptions import (ExecuteRuntimeError, ScriptRuntimeError,
                          NetworkError)
from .strings import mask_string


def execute(cmd, workdir=None, can_fail=False, mask_list=None,
            use_shell=False):
    """
    Runs shell command cmd. If can_fail is set to False
    ExecuteRuntimeError is raised if command returned non-zero return
    code. Otherwise
    """
    mask_list = mask_list or []
    repl_list = [("'","'\\''")]

    if type(cmd) is not types.StringType:
        import pipes
        masked = ' '.join((pipes.quote(i) for i in cmd))
    else:
        masked = cmd
    masked = mask_string(masked, mask_list, repl_list)
    logging.debug("Executing command: %s" % masked)

    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, cwd=workdir,
                            shell=use_shell, close_fds=True)
    out, err = proc.communicate()
    logging.debug("rc: %s" % proc.returncode)
    logging.debug("stdout:\n%s" % mask_string(out, mask_list, repl_list))
    logging.debug("stderr:\n%s" % mask_string(err, mask_list, repl_list))

    if not can_fail and proc.returncode != 0:
        msg = 'Failed to execute command: %s' % masked
        raise ExecuteRuntimeError(msg, stdout=out, stderr=err)
    return proc.returncode, out


class ScriptRunner(object):
    _pkg_search = 'rpm -q'

    def __init__(self, ip=None):
        self.script = []
        self.ip = ip

    def append(self, s):
        self.script.append(s)

    def clear(self):
        self.script = []

    def execute(self, logerrors=True, maskList=None):
        maskList = maskList or []
        script = "\n".join(self.script)
        logging.debug("# ============ ssh : %r =========="%self.ip)

        _PIPE = subprocess.PIPE  # pylint: disable=E1101
        if self.ip:
            cmd = ["ssh", "-o", "StrictHostKeyChecking=no",
                          "-o", "UserKnownHostsFile=/dev/null",
                          "root@%s" % self.ip, "bash -x"]
        else:
            cmd = ["bash", "-x"]
        obj = subprocess.Popen(cmd, stdin=_PIPE, stdout=_PIPE,
                               stderr=_PIPE, close_fds=True,
                               shell=False)

        replace_list = [("'","'\\''")]
        logging.debug(mask_string(script, maskList, replace_list))
        script = "function t(){ exit $? ; } \n trap t ERR \n" + script
        stdoutdata, stderrdata = obj.communicate(script)
        logging.debug("============ STDOUT ==========")
        logging.debug(mask_string(stdoutdata, maskList, replace_list))
        returncode = obj.returncode
        if returncode:
            if logerrors:
                logging.error("============= STDERR ==========")
                logging.error(mask_string(stderrdata, maskList,
                                          replace_list))

            pattern = (r'^ssh\:')
            if re.search(pattern, stderrdata):
                raise NetworkError(stderrdata, stdout=stdoutdata,
                                   stderr=stderrdata)
            else:
                msg = 'Error running remote script: %s' % stdoutdata
                raise ScriptRuntimeError(msg, stdout=stdoutdata,
                                         stderr=stderrdata)
        return returncode, stdoutdata

    def template(self, src, dst, varsdict):
        with open(src) as fp:
            content = fp.read() % varsdict
            self.append("cat > %s <<- EOF\n%s\nEOF\n" % (dst, content))

    def if_not_exists(self, path, command):
        self.append("[ -e %s ] || %s" % (path, command))

    def if_exists(self, path, command):
        self.append("[ -e %s ] && %s" % (path, command))

    def if_installed(self, pkg, command):
        self.append("%s %s && %s" % (self._pkg_search, pkg, command))

    def if_not_installed(self, pkg, command):
        self.append("%s %s || %s" % (self._pkg_search, pkg, command))

    def chown(self, target, uid, gid):
        self.append("chown %s:%s %s" % (uid, gid, target))

    def chmod(self, target, mode):
        self.append("chown %s %s" % (mode, target))
