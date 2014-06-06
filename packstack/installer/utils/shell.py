# -*- coding: utf-8 -*-

import re
import os
import types
import logging
import subprocess

from ..exceptions import (ExecuteRuntimeError, ScriptRuntimeError,
                          NetworkError)
from .strings import mask_string


block_fmt = ("\n============= %(title)s ==========\n%(content)s\n"
             "======== END OF %(title)s ========")


def execute(cmd, workdir=None, can_fail=True, mask_list=None,
            use_shell=False, log=True):
    """
    Runs shell command cmd. If can_fail is set to False
    ExecuteRuntimeError is raised if command returned non-zero return
    code. Otherwise
    """
    mask_list = mask_list or []
    repl_list = [("'", "'\\''")]

    if not isinstance(cmd, types.StringType):
        import pipes
        masked = ' '.join((pipes.quote(i) for i in cmd))
    else:
        masked = cmd
    masked = mask_string(masked, mask_list, repl_list)
    if log:
        logging.info("Executing command:\n%s" % masked)
    environ = os.environ
    environ['LANG'] = 'en_US.UTF8'
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, cwd=workdir,
                            shell=use_shell, close_fds=True,
                            env=environ)
    out, err = proc.communicate()
    masked_out = mask_string(out, mask_list, repl_list)
    masked_err = mask_string(err, mask_list, repl_list)
    if log:
        logging.debug(block_fmt % {'title': 'STDOUT', 'content': masked_out})

    if proc.returncode:
        if log:
            logging.debug(block_fmt % {'title': 'STDERR',
                                       'content': masked_err})
        if can_fail:
            msg = ('Failed to execute command, '
                   'stdout: %s\nstderr: %s' %
                   (masked_out, masked_err))
            raise ExecuteRuntimeError(msg, stdout=out, stderr=err)
    return proc.returncode, out


class ScriptRunner(object):
    _pkg_search = 'rpm -q --whatprovides'

    def __init__(self, ip=None):
        self.script = []
        self.ip = ip

    def append(self, s):
        self.script.append(s)

    def clear(self):
        self.script = []

    def execute(self, can_fail=True, mask_list=None, log=True):
        mask_list = mask_list or []
        repl_list = [("'", "'\\''")]
        script = "\n".join(self.script)

        masked = mask_string(script, mask_list, repl_list)
        if log:
            logging.info("[%s] Executing script:\n%s" %
                         (self.ip or 'localhost', masked))

        _PIPE = subprocess.PIPE  # pylint: disable=E1101
        if self.ip:
            cmd = ["ssh", "-o", "StrictHostKeyChecking=no",
                          "-o", "UserKnownHostsFile=/dev/null",
                          "root@%s" % self.ip, "bash -x"]
        else:
            cmd = ["bash", "-x"]
        environ = os.environ
        environ['LANG'] = 'en_US.UTF8'
        obj = subprocess.Popen(cmd, stdin=_PIPE, stdout=_PIPE, stderr=_PIPE,
                               close_fds=True, shell=False,
                                env=environ)

        script = "function t(){ exit $? ; } \n trap t ERR \n" + script
        out, err = obj.communicate(script)
        masked_out = mask_string(out, mask_list, repl_list)
        masked_err = mask_string(err, mask_list, repl_list)
        if log:
            logging.debug(block_fmt % {'title': 'STDOUT',
                                       'content': masked_out})

        if obj.returncode:
            if log:
                logging.debug(block_fmt % {'title': 'STDERR',
                                           'content': masked_err})
            if can_fail:
                pattern = (r'^ssh\:')
                if re.search(pattern, err):
                    raise NetworkError(masked_err, stdout=out, stderr=err)
                else:
                    msg = ('Failed to run remote script, '
                           'stdout: %s\nstderr: %s' %
                           (masked_out, masked_err))
                    raise ScriptRuntimeError(msg, stdout=out, stderr=err)
        return obj.returncode, out

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
        self.append("chmod %s %s" % (mode, target))
