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

                  ]


    groupDict = { "GROUP_NAME"            : "QPIDLANCE",
                  "DESCRIPTION"           : "QPID Config parameters",
                  "PRE_CONDITION"         : "CONFIG_NOVA_INSTALL",
                  "PRE_CONDITION_MATCH"   : "y",
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
                  "PRE_CONDITION"         : "CONFIG_QPID_ENABLE_SSL",
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
    manifestfile = "%s_qpid.pp"%config['CONFIG_QPID_HOST']
    manifestdata = ""
    ssl_manifestdata = ""
    server = utils.ScriptRunner(config['CONFIG_QPID_HOST'])
    ports = set(["'5672'"])
    if config['CONFIG_QPID_ENABLE_SSL'] == 'y':
        ports.add("'%s'" % (config['CONFIG_QPID_SSL_PORT']))
        config['CONFIG_QPID_ENABLE_SSL'] = 'true'
        if config['CONFIG_QPID_SSL_SELF_SIGNED'] == 'y':
            server.append( "openssl req -batch -new -x509 -nodes -keyout %s -out %s -days 1095"
                % (config['CONFIG_QPID_SSL_KEY_FILE'], config['CONFIG_QPID_SSL_CERT_FILE']) )
            server.execute()
        ssl_manifestdata = getManifestTemplate('qpid_ssl.pp')
    else:
        #Set default values 
        config['CONFIG_QPID_SSL_PORT'] = "5671"
        config['CONFIG_QPID_SSL_CERT_FILE'] = ""
        config['CONFIG_QPID_SSL_KEY_FILE'] = ""
        config['CONFIG_QPID_NSS_CERTDB_PW'] = ""
        config['CONFIG_QPID_ENABLE_SSL'] = 'false'

    manifestdata = getManifestTemplate('qpid.pp')
    manifestdata += ssl_manifestdata

    #All hosts should be able to talk to qpid
    hosts = ["'%s'" % i for i in filtered_hosts(config, exclude=False)]
    # if the rule already exists for one port puppet will fail
    # we have to add them by separate
    for port in ports:
        config['FIREWALL_ALLOWED'] = ','.join(hosts)
        config['FIREWALL_SERVICE_NAME'] = "qpid - %s" % (port)
        config['FIREWALL_PORTS'] = port
        manifestdata += getManifestTemplate("firewall.pp")

    appendManifestFile(manifestfile, manifestdata, 'pre')
