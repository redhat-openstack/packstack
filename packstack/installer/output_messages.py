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

'''
external text file to hold all user visible text.
info messages begins with INFO_ and error msg with ERR_

any text with %s inside it, has dynamic parameters inside.
please don't remove the %s from the text.
you can relocate %s position in the text as long as the context is kept.
\n means new line in the text
\ at the end of a line lets you continue the text in a new line

DONT CHANGE any of the params names (in UPPER-CASE)
they are used in the engine-setup.py
'''     # noqa: W605

from packstack.installer import basedefs

INFO_HEADER = "Welcome to the %s setup utility" % basedefs.APP_NAME
INFO_INSTALL_SUCCESS = "\n **** Installation completed successfully ******\n"
INFO_INSTALL = "Installing:"
INFO_DSPLY_PARAMS = "\n%s will be installed using the following configuration:" % basedefs.APP_NAME
INFO_USE_PARAMS = "Proceed with the configuration listed above"
INFO_DONE = "DONE"
INFO_ERROR = "ERROR"
INFO_LOG_FILE_PATH = "The installation log file is available at: %s"
INFO_MANIFEST_PATH = "The generated manifests are available at: %s"
INFO_ADDTIONAL_MSG = "Additional information:"
INFO_ADDTIONAL_MSG_BULLET = " * %s"
INFO_CONF_PARAMS_PASSWD_CONFIRM_PROMPT = "Confirm password"
INFO_VAL_PATH_SPACE = "Error: mount point %s contains only %s of available space while a minimum of %s is required"
INFO_VAL_NOT_INTEGER = "Error: value is not an integer"
INFO_VAL_PORT_NOT_RANGE = "Error: port is outside the range of %i - 65535"
INFO_VAL_STRING_EMPTY = "Warning: The %s parameter is empty"
INFO_VAL_NOT_IN_OPTIONS = "Error: response is not part of the following accepted answers: %s"
INFO_VAL_NOT_DOMAIN = "Error: domain is not a valid domain name"
INFO_VAL_NOT_USER = "Error: user name contains illegal characters"
INFO_VAL_PORT_OCCUPIED = "Error: TCP Port %s is already open by %s (pid: %s)"
INFO_VAL_PORT_OCCUPIED_BY_JBOSS = "Error: TCP Port %s is used by JBoss"
INFO_VAL_PASSWORD_DONT_MATCH = "Error: passwords don't match"

INFO_CHANGED_VALUE = ("Packstack changed given value %s to required "
                      "value %s")
WARN_VAL_IS_HOSTNAME = ("Warning: Packstack failed to change given "
                        "hostname %s to IP address. Note that some "
                        "services might not run correctly when hostname"
                        " is used.")

INFO_STRING_LEN_LESS_THAN_MIN = "String length is less than the minimum allowed: %s"
INFO_STRING_EXCEEDS_MAX_LENGTH = "String length exceeds the maximum length allowed: %s"
INFO_STRING_CONTAINS_ILLEGAL_CHARS = "String contains illegal characters"
INFO_CINDER_VOLUMES_EXISTS = "Did not create a cinder volume group, one already existed"
INFO_REMOVE_REMOTE_VAR = "Removing %s on %s (if it is a remote host)"

WARN_WEAK_PASS = "Warning: Weak Password."
WARN_NM_ENABLED = ("Warning: NetworkManager is active on %s. OpenStack "
                   "networking currently does not work on systems that have "
                   "the Network Manager service enabled.")
WARN_IPV6_OVS = ("Warning: IPv6 and ovs tunneling is not yet supported and "
                 "will fail on host %s see https://bugzilla.redhat.com/show_bug.cgi?id=1100360.")

ERR_PING = "Error: the provided hostname is unreachable"
ERR_SSH = "Error: could not connect to the ssh server: %s"
ERR_FILE = "Error: the provided file is not present"
ERR_CHECK_LOG_FILE_FOR_MORE_INFO = "Please check log file %s for more information"
ERR_YUM_LOCK = "Internal Error: Can't edit versionlock "
ERR_FAILED_START_SERVICE = "Error: Can't start the %s service"
ERR_FAILED_STOP_SERVICE = "Error: Can't stop the %s service"
ERR_EXP_HANDLE_PARAMS = "Failed handling user parameters input"
ERR_EXP_KEYBOARD_INTERRUPT = "Keyboard interrupt caught."
ERR_READ_RPM_VER = "Error reading version number for package %s"
ERR_EXP_READ_INPUT_PARAM = "Error while trying to read parameter %s from user."
ERR_EXP_VALIDATE_PARAM = "Error validating parameter %s from user."
ERR_EXP_HANDLE_ANSWER_FILE = "Failed handling answer file: %s"
ERR_EXP_GET_CFG_IPS = "Could not get list of available IP addresses on this host"
ERR_EXP_GET_CFG_IPS_CODES = "Failed to get list of IP addresses"
ERR_EXP_CANT_FIND_IP = "Could not find any configured IP address"
ERR_DIDNT_RESOLVED_IP = "%s did not resolve into an IP address"
ERR_IPS_NOT_CONFIGED = "Some or all of the IP addresses: (%s) which were resolved from the FQDN %s are not configured on any interface on this host"
ERR_IPS_NOT_CONFIGED_ON_INT = "The IP (%s) which was resolved from the FQDN %s is not configured on any interface on this host"
ERR_IPS_HAS_NO_PTR = "None of the IP addresses on this host(%s) holds a PTR record for the FQDN: %s"
ERR_IP_HAS_NO_PTR = "The IP %s does not hold a PTR record for the FQDN: %s"
ERR_EXP_FAILED_INIT_LOGGER = "Unexpected error: Failed to initiate logger, please check file system permission"
ERR_FAILURE = "General failure"
ERR_NO_ANSWER_FILE = "Error: Could not find file %s"
ERR_ONLY_1_FLAG = "Error: The %s flag is mutually exclusive to all other command line options"
ERR_REMOVE_REMOTE_VAR = "Error: Failed to remove directory %s on %s, it contains sensitive data and should be removed"
ERR_REMOVE_TMP_FILE = "Error: Failed to remove temporary file %s, it contains sensitive data and should be removed"
#
