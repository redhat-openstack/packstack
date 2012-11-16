"""
contains all available validation functions
"""
import common_utils as utils
import re
import logging
import output_messages
import basedefs
import types
import traceback
import os
import os.path
import tempfile
from setup_controller import Controller

def validateDirSize(path, size):
    availableSpace = utils.getAvailableSpace(_getBasePath(path))
    if availableSpace < size:
        print output_messages.INFO_VAL_PATH_SPACE % (path,
                                                     utils.transformUnits(availableSpace),
                                                     utils.transformUnits(size))
        return False
    return True

def validateInteger(param, options=[]):
    try:
        int(param)
        return True
    except:
        logging.warn("validateInteger('%s') - failed" %(param))
        print output_messages.INFO_VAL_NOT_INTEGER
        return False

def validateRe(param, options=[]):
    for regex in options:
        if re.search(regex, param):
            return True
    logging.warn("validateRe('%s') - failed" %(param))
    return False

def validatePort(param, options = []):
    #TODO: add actual port check with socket open
    logging.debug("Validating %s as a valid TCP Port" % (param))
    minVal = 0
    controller = Controller()
    isProxyEnabled = utils.compareStrIgnoreCase(controller.CONF["OVERRIDE_HTTPD_CONFIG"], "yes")
    if not isProxyEnabled:
        minVal = 1024
    if not validateInteger(param, options):
        return False
    port = int(param)
    if not (port > minVal and port < 65535) :
        logging.warn(output_messages.INFO_VAL_PORT_NOT_RANGE %(minVal))
        print output_messages.INFO_VAL_PORT_NOT_RANGE %(minVal)
        return False
    (portOpen, process, pid) = utils.isTcpPortOpen(param)
    if portOpen:
        logging.warn(output_messages.INFO_VAL_PORT_OCCUPIED % (param, process, pid))
        print output_messages.INFO_VAL_PORT_OCCUPIED % (param, process, pid)
        return False
    if isProxyEnabled and not checkAndSetHttpdPortPolicy(param):
        logging.warn(output_messages.INFO_VAL_FAILED_ADD_PORT_TO_HTTP_POLICY, port)
        print output_messages.INFO_VAL_FAILED_ADD_PORT_TO_HTTP_POLICY % port
        return False
    return True

def checkAndSetHttpdPortPolicy(port):
    def parsePorts(portsStr):
        ports = []
        for part in portsStr.split(","):
            part = part.strip().split("-")
            if len(part) > 1:
                for port in range(int(part[0]),int(part[1])):
                    ports.append(port)
            else:
                ports.append(int(part[0]))
        return ports

    newPort = int(port)
    cmd = [
        basedefs.EXEC_SEMANAGE, "port", "-l",
    ]
    out, rc = utils.execCmd(cmdList=cmd) #, "-t", "http_port_t"])
    if rc:
        return False
    httpPortsList = []
    pattern = re.compile("^http_port_t\s*tcp\s*([0-9, \-]*)$")
    for line in out.splitlines():
        httpPortPolicy = re.match(pattern, line)
        if httpPortPolicy:
            httpPortsList = parsePorts(httpPortPolicy.groups()[0])
    logging.debug("http_port_t = %s"%(httpPortsList))
    if newPort in httpPortsList:
        return True
    else:
        cmd = [
            basedefs.EXEC_SEMANAGE,
            "port",
            "-a",
            "-t", "http_port_t",
            "-p", "tcp",
            "%d"%(newPort),
        ]
        out, rc = utils.execCmd(cmdList=cmd, failOnError=False, usePipeFiles=True)
        if rc:
            logging.error(out)
            return False
    return True



def validateRemotePort(param, options = []):
    #Validate that the port is an integer betweeen 1024 and 65535
    logging.debug("Validating %s as a valid TCP Port" % (param))
    if validateInteger(param, options):
        port = int(param)
        if (port > 0 and port < 65535):
            return True
        else:
            logging.warn("validatePort('%s') - failed" %(param))
            print output_messages.INFO_VAL_PORT_NOT_RANGE

    return False

def validateStringNotEmpty(param, options=[]):
    if type(param) != types.StringType or len(param) == 0:
        logging.warn("validateStringNotEmpty('%s') - failed" %(param))
        print output_messages.INFO_VAL_STRING_EMPTY %(param)
        return False
    else:
        return True

def validateOptions(param, options=[]):
    logging.info("Validating %s as part of %s"%(param, options))
    if not validateStringNotEmpty(param, options):
        return False
    if "yes" in options and param.lower() == "y":
        return True
    if "no" in options and param.lower() == "n":
        return True
    if param.lower() in [option.lower() for option in options]:
        return True
    print output_messages.INFO_VAL_NOT_IN_OPTIONS % (", ".join(options))
    return False

def validateDomain(param, options=[]):
    """
    Validate domain name
    """
    logging.info("validating %s as a valid domain string" % (param))
    (errMsg, rc) = _validateString(param, 1, 1024, "^[\w\-\_]+\.[\w\.\-\_]+\w+$")

    # Right now we print a generic error, might want to change it in the future
    if rc != 0:
        print output_messages.INFO_VAL_NOT_DOMAIN
        return False
    else:
        return True

def validateUser(param, options=[]):
    """
    Validate Auth Username
    Setting a logical max value of 256
    """
    logging.info("validating %s as a valid user name" % (param))
    (errMsg, rc) = _validateString(param, 1, 256, "^\w[\w\.\-\_\%\@]{2,}$")

    # Right now we print a generic error, might want to change it in the future
    if rc != 0:
        print output_messages.INFO_VAL_NOT_USER
        return False
    else:
        return True

def validateRemoteHost(param, options=[]):
    """ Validate that the we are working with remote DB host
    """
    # If we received localhost, use default flow.
    # If not local, REMOTE_DB group is run.
    # It means returning True if remote, and False if local

    if "DB_REMOTE_INSTALL" in param.keys() and param["DB_REMOTE_INSTALL"] == "remote":
        return True
    else:
        return False

def validateFQDN(param, options=[]):
    logging.info("Validating %s as a FQDN"%(param))
    if not validateDomain(param,options):
        return False
    try:
        #get set of IPs
        ipAddresses = utils.getConfiguredIps()
        if len(ipAddresses) < 1:
            logging.error("Could not find any configured IP address on the host")
            raise Exception(output_messages.ERR_EXP_CANT_FIND_IP)

        #resolve fqdn
        pattern = 'Address: (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        resolvedAddresses = _getPatternFromNslookup(param, pattern)
        if len(resolvedAddresses) < 1:
            logging.error("Failed to resolve %s"%(param))
            print output_messages.ERR_DIDNT_RESOLVED_IP%(param)
            return False

        #string is generated here since we use it in all latter error messages
        prettyString = " ".join(["%s"%string for string in resolvedAddresses])

        #compare found IP with list of local IPs and match.
        if not resolvedAddresses.issubset(ipAddresses):
            logging.error("the following address(es): %s are not configured on this host"%(prettyString))
            #different grammar for plural and single
            if len(resolvedAddresses) > 1:
                print output_messages.ERR_IPS_NOT_CONFIGED%(prettyString, param)
            else:
                print output_messages.ERR_IPS_NOT_CONFIGED_ON_INT%(prettyString, param)
            return False

        #reverse resolved IP and compare with given fqdn
        counter = 0
        pattern = '[\w\.-]+\s+name\s\=\s([\w\.\-]+)\.'
        for address in resolvedAddresses:
            addressSet = _getPatternFromNslookup(address, pattern)
            reResolvedAddress = None
            if len(addressSet) > 0:
                reResolvedAddress = addressSet.pop()
            if reResolvedAddress == param:
                counter += 1
            else:
                logging.warn("%s did not reverse-resolve into %s"%(address,param))
        if counter < 1:
            logging.error("The following addresses: %s did not reverse resolve into %s"%(prettyString, param))
            #different grammar for plural and single
            if len(resolvedAddresses) > 1:
                print output_messages.ERR_IPS_HAS_NO_PTR%(prettyString, param)
            else:
                print output_messages.ERR_IP_HAS_NO_PTR%(prettyString, param)
            return False

        #conditions passed
        return True
    except:
        logging.error(traceback.format_exc())
        raise

def validateFile(param, options=[]):
    """
    Check that provided param is a file
    """
    if not validateStringNotEmpty(param):
        return False

    if not os.path.isfile(param):
        print "\n" + output_messages.ERR_FILE + ".\n"
        return False

    return True

def validatePing(param, options=[]):
    """
    Check that provided host answers to ping
    """
    if validateStringNotEmpty(param):
        cmd = [
            "/bin/ping",
            "-c", "1",
            "%s" % param,
        ]
        out, rc = utils.execCmd(cmdList=cmd)
        if rc == 0:
            return True

    print "\n" + output_messages.ERR_PING + " %s .\n"%param
    return False

def validateMultiPing(param, options=[]):
    if validateStringNotEmpty(param):
        hosts = param.split(",")
        for host in hosts:
            if validatePing(host.strip()) == False:
                return False
        return True
    print "\n" + output_messages.ERR_PING + ".\n"
    return False

def _validateString(string, minLen, maxLen, regex=".*"):
    """
    Generic func to verify a string
    match its min/max length
    and doesn't contain illegal chars

    The func returns various return codes according to the error
    plus a default error message
    the calling func can decide if to use to default error msg
    or to use a more specific one according the RC.
    Return codes:
    1 - string length is less than min
    2 - string length is more tham max
    3 - string contain illegal chars
    0 - success
    """
    # String length is less than minimum allowed
    if len(string) < minLen:
        msg = output_messages.INFO_STRING_LEN_LESS_THAN_MIN % (minLen)
        return(msg, 1)
    # String length is more than max allowed
    elif len(string) > maxLen:
        msg = output_messages.INFO_STRING_EXCEEDS_MAX_LENGTH % (maxLen)
        return(msg, 2)
    # String contains illegal chars
    elif not utils.verifyStringFormat(string, regex):
        return(output_messages.INFO_STRING_CONTAINS_ILLEGAL_CHARS, 3)
    else:
        # Success
        return (None, 0)

def _getPatternFromNslookup(address, pattern):
    rePattern = re.compile(pattern)
    addresses = set()
    output = utils.nslookup(address)
    list = output.splitlines()
    #do not go over the first 2 lines in nslookup output
    for line in list[2:]:
        found = rePattern.search(line)
        if found:
            foundAddress = found.group(1)
            logging.debug("%s resolved into %s"%(address, foundAddress))
            addresses.add(foundAddress)
    return addresses

def _getBasePath(path):
    if os.path.exists(path):
        return path

    # Iterate up in the tree structure until we get an
    # existing path
    return _getBasePath(os.path.dirname(path.rstrip("/")))

def _isPathWriteable(path):
    try:
        logging.debug("attempting to write temp file to %s" % (path))
        tempfile.TemporaryFile(dir=path)
        return True
    except:
        logging.warning(traceback.format_exc())
        logging.warning("%s is not writeable" % path)
        return False

def r_validateIF(server, device):
    """ Validate that a network interface exists on a remote host """
    server.append("ifconfig %s || ( echo Device %s does not exist && exit 1 )"%(device, device))

def r_validateDevice(server, device=None):
    if device:
        # the device MUST exist
        server.append('ls -l /dev/%s'%device)

        # if it is not mounted then we can use it
        server.append('grep "/dev/%s " /proc/self/mounts || exit 0'%device)

        # if it is mounted then the mount point has to be in /srv/node
        server.append('grep "/dev/%s /srv/node" /proc/self/mounts && exit 0'%device)
        
        # if we got here without exiting then we can't use this device
        server.append('exit 1')
    return False

