"""
Installs and configures qpid
"""

import logging
import uuid
import os

from packstack.installer import validators
from packstack.installer import basedefs
from packstack.installer import utils

from packstack.modules.common import filtered_hosts
from packstack.modules.ospluginutils import gethostlist,\
                                            getManifestTemplate,\
                                            appendManifestFile

# Controller object will be initialized from main flow
controller = None

# Plugin name
PLUGIN_NAME = "OS-QPID"
PLUGIN_NAME_COLORED = utils.color_text(PLUGIN_NAME, 'blue')

logging.debug("plugin %s loaded", __name__)

def initConfig(controllerObject):
    global controller
    controller = controllerObject
    logging.debug("Adding OpenStack QPID configuration")
    paramsList = [
                  {"CMD_OPTION"      : "qpid-host",
                   "USAGE"           : "The IP address of the server on which to install the QPID service",
                   "PROMPT"          : "Enter the IP address of the QPID service",
                   "OPTION_LIST"     : [],
                   "VALIDATORS"      : [validators.validate_ssh],
                   "DEFAULT_VALUE"   : utils.get_localhost_ip(),
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_QPID_HOST",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "qpid-enable-ssl",
                   "USAGE"           : "Enable SSL for the QPID service",
                   "PROMPT"          : "Enable SSL for the QPID service?",
                   "OPTION_LIST"     : ["y", "n"],
                   "VALIDATORS"      : [validators.validate_options],
                   "DEFAULT_VALUE"   : "n",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": False,
                   "CONF_NAME"       : "CONFIG_QPID_ENABLE_SSL",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "qpid-enable-auth",
                   "USAGE"           : "Enable Authentication for the QPID service",
                   "PROMPT"          : "Enable Authentication for the QPID service?",
                   "OPTION_LIST"     : ["y", "n"],
                   "VALIDATORS"      : [validators.validate_options],
                   "DEFAULT_VALUE"   : "n",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": False,
                   "CONF_NAME"       : "CONFIG_QPID_ENABLE_AUTH",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },


                  ]


    groupDict = { "GROUP_NAME"            : "QPIDLANCE",
                  "DESCRIPTION"           : "QPID Config parameters",
                  "PRE_CONDITION"         : check_enabled,
                  "PRE_CONDITION_MATCH"   : True,
                  "POST_CONDITION"        : False,
                  "POST_CONDITION_MATCH"  : True}

    controller.addGroup(groupDict, paramsList)

    paramsList = [
                  {"CMD_OPTION"      : "qpid-nss-certdb-pw",
                   "USAGE"           : "The password for the NSS certificate database of the QPID service",
                   "PROMPT"          : "Enter the password for NSS certificate database",
                   "OPTION_LIST"     : [],
                   "VALIDATORS"      : [validators.validate_not_empty],
                   "DEFAULT_VALUE"   : uuid.uuid4().hex[:32],
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_QPID_NSS_CERTDB_PW",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "qpid-ssl-port",
                   "USAGE"           : "The port in which the QPID service listens to SSL connections",
                   "PROMPT"          : "Enter the SSL port for the QPID service",
                   "OPTION_LIST"     : [],
                   "VALIDATORS"      : [validators.validate_not_empty],
                   "DEFAULT_VALUE"   : "5671",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_QPID_SSL_PORT",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "qpid-ssl-cert-file",
                   "USAGE"           : "The filename of the certificate that the QPID service is going to use",
                   "PROMPT"          : "Enter the filename of the SSL certificate for the QPID service",
                   "OPTION_LIST"     : [],
                   "VALIDATORS"      : [validators.validate_not_empty],
                   "DEFAULT_VALUE"   : "/etc/pki/tls/certs/qpid_selfcert.pem",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_QPID_SSL_CERT_FILE",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "qpid-ssl-key-file",
                   "USAGE"           : "The filename of the private key that the QPID service is going to use",
                   "PROMPT"          : "Enter the private key filename",
                   "OPTION_LIST"     : [],
                   "VALIDATORS"      : [validators.validate_not_empty],
                   "DEFAULT_VALUE"   : "/etc/pki/tls/private/qpid_selfkey.pem",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_QPID_SSL_KEY_FILE",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "qpid-ssl-self-signed",
                   "USAGE"           : "Auto Generates self signed SSL certificate and key",
                   "PROMPT"          : "Generate Self Signed SSL Certificate",
                   "OPTION_LIST"     : ["y","n"],
                   "VALIDATORS"      : [validators.validate_not_empty],
                   "DEFAULT_VALUE"   : "y",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_QPID_SSL_SELF_SIGNED",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                 ]

    groupDict = { "GROUP_NAME"            : "QPIDSSL",
                  "DESCRIPTION"           : "QPID Config SSL parameters",
                  "PRE_CONDITION"         : check_ssl_enabled,
                  "PRE_CONDITION_MATCH"   : True,
                  "POST_CONDITION"        : False,
                  "POST_CONDITION_MATCH"  : True}

    controller.addGroup(groupDict, paramsList)

    paramsList = [
                  {"CMD_OPTION"      : "qpid-auth-user",
                   "USAGE"           : "User for qpid authentication",
                   "PROMPT"          : "Enter the user for qpid authentication",
                   "OPTION_LIST"     : [],
                   "VALIDATORS"      : [validators.validate_not_empty],
                   "DEFAULT_VALUE"   : "qpid_user",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_QPID_AUTH_USER",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "qpid-auth-password",
                   "USAGE"           : "Password for user authentication",
                   "PROMPT"          : "Enter the password for user authentication",
                   "OPTION_LIST"     : ["y", "n"],
                   "VALIDATORS"      : [validators.validate_not_empty],
                   "DEFAULT_VALUE"   : uuid.uuid4().hex[:16],
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_QPID_AUTH_PASSWORD",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },

                  ]

    groupDict = { "GROUP_NAME"            : "QPIDAUTH",
                  "DESCRIPTION"           : "QPID Config Athentication parameters",
                  "PRE_CONDITION"         : "CONFIG_QPID_ENABLE_AUTH",
                  "PRE_CONDITION_MATCH"   : "y",
                  "POST_CONDITION"        : False,
                  "POST_CONDITION_MATCH"  : True}


    controller.addGroup(groupDict, paramsList)
def check_ssl_enabled(config):
    return check_enabled(config) and config.get('CONFIG_QPID_ENABLE_SSL') == 'y'


def check_enabled(config):
    return (config.get('CONFIG_NOVA_INSTALL') == 'y' or
        config.get('CONFIG_QPID_HOST') != '')

def initSequences(controller):
    qpidsteps = [
             {'title': 'Adding QPID manifest entries', 'functions':[createmanifest]}
    ]
    controller.addSequence("Installing QPID", [], [], qpidsteps)

def createmanifest(config):
    manifestfile = "%s_qpid.pp"%config['CONFIG_QPID_HOST']
    manifestdata = ""
    ssl_manifestdata = ""
    server = utils.ScriptRunner(config['CONFIG_QPID_HOST'])
    if config['CONFIG_QPID_ENABLE_SSL'] == 'y':
        config['CONFIG_QPID_ENABLE_SSL'] = 'true'
        config['CONFIG_QPID_PROTOCOL'] = 'ssl'
        config['CONFIG_QPID_CLIENTS_PORT'] = "5671"
        if config['CONFIG_QPID_SSL_SELF_SIGNED'] == 'y':
            server.append( "openssl req -batch -new -x509 -nodes -keyout %s -out %s -days 1095"
                % (config['CONFIG_QPID_SSL_KEY_FILE'], config['CONFIG_QPID_SSL_CERT_FILE']) )
            server.execute()
        ssl_manifestdata = getManifestTemplate('qpid_ssl.pp')
    else:
        #Set default values
        config['CONFIG_QPID_CLIENTS_PORT'] = "5672"
        config['CONFIG_QPID_SSL_PORT'] = "5671"
        config['CONFIG_QPID_SSL_CERT_FILE'] = ""
        config['CONFIG_QPID_SSL_KEY_FILE'] = ""
        config['CONFIG_QPID_NSS_CERTDB_PW'] = ""
        config['CONFIG_QPID_ENABLE_SSL'] = 'false'
        config['CONFIG_QPID_PROTOCOL'] = 'tcp'

    manifestdata = getManifestTemplate('qpid.pp')
    manifestdata += ssl_manifestdata

    if config['CONFIG_QPID_ENABLE_AUTH'] == 'y':
        manifestdata += getManifestTemplate('qpid_auth.pp')
    else:
        config['CONFIG_QPID_AUTH_PASSWORD'] = 'guest'
        config['CONFIG_QPID_AUTH_USER'] = 'guest'

    #All hosts should be able to talk to qpid
    config['FIREWALL_SERVICE_NAME'] = "qpid"
    config['FIREWALL_PORTS'] =  "['5671', '5672']"
    config['FIREWALL_CHAIN'] = "INPUT"
    config['FIREWALL_PROTOCOL'] = 'tcp'
    for host in filtered_hosts(config, exclude=False):
        config['FIREWALL_ALLOWED'] = "'%s'" % host
        config['FIREWALL_SERVICE_ID'] = "qpid_%s" % host
        manifestdata += getManifestTemplate("firewall.pp")

    appendManifestFile(manifestfile, manifestdata, 'pre')
