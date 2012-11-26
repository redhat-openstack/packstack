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
'''

import basedefs

#####################
####INFO MESSAGES####
#####################

INFO_HEADER="Welcome to %s setup utility" % basedefs.APP_NAME
INFO_INSTALL_SUCCESS="\n **** Installation completed successfully ******\n\n     (Please allow %s a few moments to start up.....)\n" % basedefs.APP_NAME
INFO_INSTALL="Installing:"
INFO_DSPLY_PARAMS="\n%s will be installed using the following configuration:" % basedefs.APP_NAME
INFO_USE_PARAMS="Proceed with the configuration listed above"
INFO_DONE="DONE"
INFO_ERROR="ERROR"
INFO_LOG_FILE_PATH="The installation log file is available at: %s"
INFO_ADDTIONAL_MSG="Additional information:"
INFO_ADDTIONAL_MSG_BULLET=" * %s"
INFO_CONF_PARAMS_PASSWD_CONFIRM_PROMPT="Confirm password"
INFO_VAL_PATH_SPACE="Error: mount point %s contains only %s of available space while a minimum of %s is required"
INFO_VAL_NOT_INTEGER="Error: value is not an integer"
INFO_VAL_PORT_NOT_RANGE="Error: port is outside the range of %i - 65535"
INFO_VAL_STRING_EMPTY="Warning: The %s parameter is empty"
INFO_VAL_NOT_IN_OPTIONS="Error: response is not part of the following accepted answers: %s"
INFO_VAL_NOT_DOMAIN="Error: domain is not a valid domain name"
INFO_VAL_NOT_USER="Error: user name contains illegal characters"
INFO_VAL_PORT_OCCUPIED="Error: TCP Port %s is already open by %s (pid: %s)"
INFO_VAL_PORT_OCCUPIED_BY_JBOSS="Error: TCP Port %s is used by JBoss"
INFO_VAL_PASSWORD_DONT_MATCH="Error: passwords don't match"

INFO_STRING_LEN_LESS_THAN_MIN="String length is less than the minimum allowed: %s"
INFO_STRING_EXCEEDS_MAX_LENGTH="String length exceeds the maximum length allowed: %s"
INFO_STRING_CONTAINS_ILLEGAL_CHARS="String contains illegal characters"

WARN_WEAK_PASS="Warning: Weak Password."

ERR_PING = "Error: the provided hostname is unreachable"
ERR_FILE = "Error: the provided file is not present"
ERR_CHECK_LOG_FILE_FOR_MORE_INFO="Please check log file %s for more information"
ERR_YUM_LOCK="Internal Error: Can't edit versionlock "
ERR_FAILED_START_SERVICE = "Error: Can't start the %s service"
ERR_FAILED_STOP_SERVICE = "Error: Can't stop the %s service"
ERR_EXP_HANDLE_PARAMS="Failed handling user parameters input"
ERR_EXP_KEYBOARD_INTERRUPT="Keyboard interrupt caught."
ERR_READ_RPM_VER="Error reading version number for package %s"
ERR_EXP_READ_INPUT_PARAM="Error while trying to read parameter %s from user."
ERR_EXP_HANDLE_ANSWER_FILE="Failed handling answer file: %s"
ERR_EXP_GET_CFG_IPS="Could not get list of available IP addresses on this host"
ERR_EXP_GET_CFG_IPS_CODES="Failed to get list of IP addresses"
ERR_EXP_CANT_FIND_IP="Could not find any configured IP address"
ERR_DIDNT_RESOLVED_IP="%s did not resolve into an IP address"
ERR_IPS_NOT_CONFIGED="Some or all of the IP addresses: (%s) which were resolved from the FQDN %s are not configured on any interface on this host"
ERR_IPS_NOT_CONFIGED_ON_INT="The IP (%s) which was resolved from the FQDN %s is not configured on any interface on this host"
ERR_IPS_HAS_NO_PTR="None of the IP addresses on this host(%s) holds a PTR record for the FQDN: %s"
ERR_IP_HAS_NO_PTR="The IP %s does not hold a PTR record for the FQDN: %s"
ERR_EXP_FAILED_INIT_LOGGER="Unexpected error: Failed to initiate logger, please check file system permission"
ERR_RC_CODE="Return Code is not zero"
ERR_FAILURE="General failure"
ERR_NO_ANSWER_FILE="Error: Could not find file %s"

# 
INFO_KEYSTONERC="To use the command line tools simply source the keystonerc_* files created here"

