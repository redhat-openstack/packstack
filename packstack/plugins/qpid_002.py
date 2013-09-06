"""
Installs and configures qpid
"""

import logging
import uuid
import os

from packstack.installer import validators
from packstack.installer import basedefs
from packstack.installer import utils

from packstack.modules.ospluginutils import getManifestTemplate, appendManifestFile

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
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_QPID_ENABLE_SSL",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "qpid-nss-certdb-dir",
                   "USAGE"           : "The directory path in which the NSS certificate database for the QPID service is stored",
                   "PROMPT"          : "Enter directoy path of the NSS certificate database",
                   "OPTION_LIST"     : [],
                   "VALIDATORS"      : [validators.validate_not_empty],
                   "DEFAULT_VALUE"   : "/etc/pki/nssdb",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_QPID_NSS_CERTDB_DIR",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
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
                  {"CMD_OPTION"      : "qpid-nss-certdb-pw-file",
                   "USAGE"           : "The file in which the password of the NSS certificate database for the QPID service is stored",
                   "PROMPT"          : "Enter the path of the password file for the NSS certificate database",
                   "OPTION_LIST"     : [],
                   "VALIDATORS"      : [validators.validate_not_empty],
                   "DEFAULT_VALUE"   : "/etc/pki/nssdb/password.conf",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_QPID_NSS_CERTDB_PW_FILE",
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
                  {"CMD_OPTION"      : "qpid-nss-cert-name",
                   "USAGE"           : "The name of the certificate that the QPID service is going to use",
                   "PROMPT"          : "Enter the name of the NSS certificate for the QPID service",
                   "OPTION_LIST"     : [],
                   "VALIDATORS"      : [validators.validate_not_empty],
                   "DEFAULT_VALUE"   : "qpid_self_signed",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_QPID_NSS_CERT_NAME",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "qpid-ssl-cert-file",
                   "USAGE"           : "The filename of the certificate that the QPID service is going to use",
                   "PROMPT"          : "Enter the filename of the SSL certificate for the QPID service",
                   "OPTION_LIST"     : [],
                   "VALIDATORS"      : [validators.validate_not_empty],
                   "DEFAULT_VALUE"   : "/etc/pki/tls/certs/selfcert.pem",
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
                   "DEFAULT_VALUE"   : "/etc/pki/tls/private/selfkey.pem",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_QPID_SSL_KEY_FILE",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "qpid-ssl-batch",
                   "USAGE"           : "Auto Generates self signed SSL certificate and key",
                   "PROMPT"          : "Enable SSL Cert Batch Generation ",
                   "OPTION_LIST"     : ["y","n"],
                   "VALIDATORS"      : [validators.validate_not_empty],
                   "DEFAULT_VALUE"   : "y",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_QPID_SSL_BATCH",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                 ]

    groupDict = { "GROUP_NAME"            : "QPIDLANCE",
                  "DESCRIPTION"           : "QPID Config parameters",
                  "PRE_CONDITION"         : "CONFIG_NOVA_INSTALL",
                  "PRE_CONDITION_MATCH"   : "y",
                  "POST_CONDITION"        : False,
                  "POST_CONDITION_MATCH"  : True}

    controller.addGroup(groupDict, paramsList)


def initSequences(controller):
    # If we don't want Nova we don't need qpid
    if controller.CONF['CONFIG_NOVA_INSTALL'] != 'y':
        return
    qpidsteps = [
             {'title': 'Adding QPID manifest entries', 'functions':[createmanifest]}
    ]
    controller.addSequence("Installing QPID", [], [], qpidsteps)

def createmanifest(config):
    if controller.CONF['CONFIG_QPID_ENABLE_SSL'] == 'y':
        controller.CONF['CONFIG_QPID_ENABLE_SSL'] = 'true'
    else:
        controller.CONF['CONFIG_QPID_ENABLE_SSL'] = 'false'
        
    manifestfile = "%s_qpid.pp"%controller.CONF['CONFIG_QPID_HOST']
    manifestdata = getManifestTemplate("qpid.pp")
    appendManifestFile(manifestfile, manifestdata, 'pre')

def genSelfSignedCerts():
    keyFile = controller.CONF['CONFIG_QPID_SSL_CERT_FILE']
    certFile = controller.CONF['CONFIG_QPID_SSL_KEY_FILE']
    os.system( "openssl req -batch -new -x509 -nodes -keyout %s -out %s -days 1095" % (keyFile, certFile) )
