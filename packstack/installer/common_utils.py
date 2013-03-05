# -*- coding: utf-8 -*-

"""
contains all common and re-usable code for rhevm-setup and sub packages
"""
import grp
import pwd
import logging
import subprocess
import re
import traceback
import os
import datetime
import types
import time
import socket
import tempfile

import basedefs
import output_messages
from .exceptions import NetworkError, ScriptRuntimeError



def getColoredText (text, color):
    ''' gets text string and color
        and returns a colored text.
        the color values are RED/BLUE/GREEN/YELLOW
        everytime we color a text, we need to disable
        the color at the end of it, for that
        we use the NO_COLOR chars.
    '''
    return color + text + basedefs.NO_COLOR

def execCmd(cmdList, cwd=None, failOnError=False, msg=output_messages.ERR_RC_CODE, maskList=[], useShell=False, usePipeFiles=False):
    """
    Run external shell command with 'shell=false'
    receives a list of arguments for command line execution
    """
    # All items in the list needs to be strings, otherwise the subprocess will fail
    cmd = [str(item) for item in cmdList]

    # We need to join cmd list into one string so we can look for passwords in it and mask them
    logCmd = _maskString((' '.join(cmd)), maskList)
    logging.debug("Executing command --> '%s'"%(logCmd))

    stdErrFD = subprocess.PIPE
    stdOutFD = subprocess.PIPE
    stdInFD = subprocess.PIPE

    if usePipeFiles:
        (stdErrFD, stdErrFile) = tempfile.mkstemp(dir="/tmp")
        (stdOutFD, stdOutFile) = tempfile.mkstemp(dir="/tmp")
        (stdInFD, stdInFile) = tempfile.mkstemp(dir="/tmp")

    # We use close_fds to close any file descriptors we have so it won't be copied to forked childs
    proc = subprocess.Popen(cmd, stdout=stdOutFD,
            stderr=stdErrFD, stdin=stdInFD, cwd=cwd, shell=useShell, close_fds=True)

    out, err = proc.communicate()
    if usePipeFiles:
        with open(stdErrFile, 'r') as f:
            err = f.read()
        os.remove(stdErrFile)

        with open(stdOutFile, 'r') as f:
            out = f.read()
        os.remove(stdOutFile)
        os.remove(stdInFile)

    logging.debug("output = %s"%(out))
    logging.debug("stderr = %s"%(err))
    logging.debug("retcode = %s"%(proc.returncode))
    output = out + err
    if failOnError and proc.returncode != 0:
        raise Exception(msg)
    return ("".join(output.splitlines(True)), proc.returncode)

def byLength(word1, word2):
    """
    Compars two strings by their length
    Returns:
    Negative if word2 > word1
    Positive if word1 > word2
    Zero if word1 == word 2
    """
    return len(word1) - len(word2)

def nslookup(address):
    cmd = [
        basedefs.EXEC_NSLOOKUP, address,
    ]
    #since nslookup will return 0 no matter what, the RC is irrelevant
    output, rc = execCmd(cmdList=cmd)
    return output

def getConfiguredIps():
    try:
        iplist=set()
        cmd = [
            basedefs.EXEC_IP, "addr",
        ]
        output, rc = execCmd(cmdList=cmd, failOnError=True, msg=output_messages.ERR_EXP_GET_CFG_IPS_CODES)
        ipaddrPattern=re.compile('\s+inet (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}).+')
        list=output.splitlines()
        for line in list:
            foundIp = ipaddrPattern.search(line)
            if foundIp:
                if foundIp.group(1) != "127.0.0.1":
                    ipAddr = foundIp.group(1)
                    logging.debug("Found IP Address: %s"%(ipAddr))
                    iplist.add(ipAddr)
        return iplist
    except:
        logging.error(traceback.format_exc())
        raise Exception(output_messages.ERR_EXP_GET_CFG_IPS)

def getCurrentDateTime(isUtc=None):
    now = None
    if (isUtc is not None):
        now = datetime.datetime.utcnow()
    else:
        now = datetime.datetime.now()
    return now.strftime("%Y_%m_%d_%H_%M_%S")

def verifyStringFormat(str, matchRegex):
    '''
    Verify that the string given matches the matchRegex.
    for example:
    string: 111-222
    matchRegex: \d{3}-\d{3}
    this will return true since the string matches the regex
    '''
    pattern = re.compile(matchRegex)
    result = re.match(pattern, str)
    if result == None:
        return False
    else:
        return True

def compareStrIgnoreCase(str1, str2):
    ''' compare 2 strings and ignore case
        if one of the input is not str (bool for e.g) - return normal comapre
    '''
    if type(str1) == types.StringType and type(str2) == types.StringType:
        return str1.lower() == str2.lower()
    else:
        return str1 == str2

def parseStrRegex(string, regex, errMsg):
    """
    Gets a text string and a regex pattern
    and returns the extracted sub-string
    captured.
    """
    rePattern = re.compile(regex)
    found = rePattern.search(string)
    if found:
        match = found.group(1)
        logging.debug("found new parsed string: %s"%(match))
        return match
    else:
        raise Exception(errMsg)

def _maskString(string, maskList=[]):
    """
    private func to mask passwords
    in utils
    """
    maskedStr = string
    for maskItem in maskList:
        if not maskItem: continue
        maskedStr = maskedStr.replace(maskItem, "*"*8)
        # if looking at stderr of a script, single quotes have been converted
        # to '\''
        maskedStr = maskedStr.replace(maskItem.replace("'","'\\''"), "*"*8)

    return maskedStr

def retry(func, expectedException=Exception, tries=None, timeout=None, sleep=1):
    """
    Retry a function. Wraps the retry logic so you don't have to
    implement it each time you need it.

    :param func: The callable to run.
    :param expectedException: The exception you expect to receive when the function fails.
    :param tries: The number of time to try. None\0,-1 means infinite.
    :param timeout: The time you want to spend waiting. This **WILL NOT** stop the method.
                    It will just not run it if it ended after the timeout.
    :param sleep: Time to sleep between calls in seconds.
    """
    if tries in [0, None]:
        tries = -1

    if timeout in [0, None]:
        timeout = -1

    startTime = time.time()

    while True:
        tries -= 1
        try:
            return func()
        except expectedException:
            if tries == 0:
                raise

            if (timeout > 0) and ((time.time() - startTime) > timeout):
                raise

            time.sleep(sleep)

def localHost(hostname):
    # Create an ip set of possible IPs on the machine. Set has only unique values, so
    # there's no problem with union.
    # TODO: cache the list somehow? There's no poing quering the IP configuraion all the time.
    ipset = getConfiguredIps().union(set([ "localhost", "127.0.0.1"]))
    if hostname in ipset:
        return True
    return False

# TODO: Support SystemD services
class Service():
    def __init__(self, name):
        self.wasStopped = False
        self.wasStarted = False
        self.name = name

    def isServiceAvailable(self):
        if os.path.exists("/etc/init.d/%s" % self.name):
            return True
        return False

    def start(self, raiseFailure = False):
        logging.debug("starting %s", self.name)
        (output, rc) = self._serviceFacility("start")
        if rc == 0:
            self.wasStarted = True
        elif raiseFailure:
            raise Exception(output_messages.ERR_FAILED_START_SERVICE % self.name)

        return (output, rc)

    def stop(self, raiseFailure = False):
        logging.debug("stopping %s", self.name)
        (output, rc) = self._serviceFacility("stop")
        if rc == 0:
            self.wasStopped = True
        elif raiseFailure:
                raise Exception(output_messages.ERR_FAILED_STOP_SERVICE % self.name)

        return (output, rc)

    def autoStart(self, start=True):
        mode = "on" if start else "off"
        cmd = [
            basedefs.EXEC_CHKCONFIG, self.name, mode,
        ]
        execCmd(cmdList=cmd, failOnError=True)

    def conditionalStart(self, raiseFailure = False):
        """
        Will only start if wasStopped is set to True
        """
        if self.wasStopped:
            logging.debug("Service %s was stopped. starting it again"%self.name)
            return self.start(raiseFailure)
        else:
            logging.debug("Service was not stopped. there for we're not starting it")
            return (False, False)

    def status(self):
        logging.debug("getting status for %s", self.name)
        (output, rc) = self._serviceFacility("status")
        return (output, rc)

    def _serviceFacility(self, action):
        """
        Execute the command "service NAME action"
        returns: output, rc
        """
        logging.debug("executing action %s on service %s", self.name, action)
        cmd = [
            basedefs.EXEC_SERVICE, self.name, action
        ]
        return execCmd(cmdList=cmd, usePipeFiles=True)

def chown(target,uid, gid):
    logging.debug("chown %s to %s:%s" % (target, uid, gid))
    os.chown(target, uid, gid)

def installed(rpm):
    cmd = [
        basedefs.EXEC_RPM,
        "-q",
        rpm,
    ]
    output, rc = execCmd(cmd)
    return rc == 0

def returnYes(controller):
    return "yes"

def getLocalhostIP():
    """
    Returns IP address of localhost.
    """
    # TO-DO: Will probably need to find better way to find out localhost
    #        address.

    # find nameservers
    ns_regex = re.compile('nameserver\s*(?P<ns_ip>[\d\.\:])')
    resolv, rc = execCmd(['cat /etc/resolv.conf | grep nameserver',],
                         failOnError=False, useShell=True)
    nsrvs = []
    for line in resolv.split('\n'):
        match = ns_regex.match(line.strip())
        if match:
            nsrvs.append(match.group('ns_ip'))

    # try to connect to nameservers and return own IP address
    nsrvs.append('8.8.8.8') # default to google dns
    for i in nsrvs:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect((i, 0))
            loc_ip = s.getsockname()[0]
        except socket.error:
            continue
        else:
            return loc_ip

def host2ip(hostname, allow_localhost=False):
    """
    Converts given hostname to IP address. Raises NetworkError
    if conversion failed.
    """
    try:
        ip_list = socket.gethostbyaddr(hostname)[2]
        if allow_localhost:
            return ip_list[0]
        else:
            local_ips = ('127.0.0.1', '::1')
            for ip in ip_list:
                if ip not in local_ips:
                    break
            else:
                raise NameError()
            return ip
    except NameError:
        # given hostname is localhost, return appropriate IP address
        ip = getLocalhostIP()
        if not ip:
            raise NetworkError('Failed to get local IP address.')
        return ip
    except socket.error:
        raise NetworkError('Unknown hostname %s.' % hostname)
    except Exception, ex:
        raise NetworkError('Unknown error appeared: %s' % repr(ex))

def forceIP(host, allow_localhost=False):
    host = host.strip()
    ipv4_regex = re.compile('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')
    ipv6_regex = re.compile('[abcdef\d\:]+')
    if not ipv4_regex.match(host) or not ipv6_regex.match(host):
        host = host2ip(host, allow_localhost=allow_localhost)
    return host

def getNics():
   output = subprocess.check_output('cat /proc/net/dev', shell=True)
   if output.find("eth0") != -1:
       return "eth0"
   if output.find("eth1") != -1:
       return "eth1"
   if output.find("em0") != -1:
       return "em0"
   if output.find("em1") != -1:
       return "em1"

class ScriptRunner(object):
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
        obj = subprocess.Popen(cmd, stdin=_PIPE, stdout=_PIPE, stderr=_PIPE,
                               close_fds=True, shell=False)

        logging.debug(_maskString(script, maskList))
        script = "function t(){ exit $? ; } \n trap t ERR \n" + script
        stdoutdata, stderrdata = obj.communicate(script)
        logging.debug("============ STDOUT ==========")
        logging.debug(_maskString(stdoutdata, maskList))
        returncode = obj.returncode
        if returncode:
            if logerrors:
                logging.error("============= STDERR ==========")
                logging.error(_maskString(stderrdata, maskList))

            pattern = (r'^ssh\:')
            if re.search(pattern, stderrdata):
                raise NetworkError(stderrdata)
            else:
                raise ScriptRuntimeError('Error running remote script: '
                                         '%s' % stdoutdata)
        return returncode, stdoutdata

    def template(self, src, dst, varsdict):
        with open(src) as fp:
            self.append("cat > %s <<- EOF\n%s\nEOF\n"%(dst, fp.read()%varsdict))

    def ifnotexists(self, fn, s):
        self.append("[ -e %s ] || %s"%(fn, s))

    def ifexists(self, fn, s):
        self.append("[ -e %s ] && %s"%(fn, s))
