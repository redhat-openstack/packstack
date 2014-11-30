# -*- coding: utf-8 -*-

"""
Installs and configures AMQP
"""

from packstack.installer import validators
from packstack.installer import processors
from packstack.installer import utils

from packstack.modules.common import filtered_hosts
from packstack.modules.ospluginutils import (getManifestTemplate,
                                             appendManifestFile,
                                             createFirewallResources)


# ------------- AMQP Packstack Plugin Initialization --------------

PLUGIN_NAME = "AMQP"
PLUGIN_NAME_COLORED = utils.color_text(PLUGIN_NAME, 'blue')


def initConfig(controller):
    params = [
        {"CMD_OPTION": "amqp-backend",
         "USAGE": ("Set the AMQP service backend. Allowed values are: "
                   "qpid, rabbitmq"),
         "PROMPT": "Set the AMQP service backend",
         "OPTION_LIST": ["qpid", "rabbitmq"],
         "VALIDATORS": [validators.validate_options],
         "DEFAULT_VALUE": "rabbitmq",
         "MASK_INPUT": False,
         "LOOSE_VALIDATION": False,
         "CONF_NAME": "CONFIG_AMQP_BACKEND",
         "USE_DEFAULT": False,
         "NEED_CONFIRM": False,
         "CONDITION": False,
         "DEPRECATES": ['CONFIG_AMQP_SERVER']},

        {"CMD_OPTION": "amqp-host",
         "USAGE": ("The IP address of the server on which to install the "
                   "AMQP service"),
         "PROMPT": "Enter the IP address of the AMQP service",
         "OPTION_LIST": [],
         "VALIDATORS": [validators.validate_ssh],
         "DEFAULT_VALUE": utils.get_localhost_ip(),
         "MASK_INPUT": False,
         "LOOSE_VALIDATION": True,
         "CONF_NAME": "CONFIG_AMQP_HOST",
         "USE_DEFAULT": False,
         "NEED_CONFIRM": False,
         "CONDITION": False},

        {"CMD_OPTION": "amqp-enable-ssl",
         "USAGE": "Enable SSL for the AMQP service",
         "PROMPT": "Enable SSL for the AMQP service?",
         "OPTION_LIST": ["y", "n"],
         "VALIDATORS": [validators.validate_options],
         "DEFAULT_VALUE": "n",
         "MASK_INPUT": False,
         "LOOSE_VALIDATION": False,
         "CONF_NAME": "CONFIG_AMQP_ENABLE_SSL",
         "USE_DEFAULT": False,
         "NEED_CONFIRM": False,
         "CONDITION": False},

        {"CMD_OPTION": "amqp-enable-auth",
         "USAGE": "Enable Authentication for the AMQP service",
         "PROMPT": "Enable Authentication for the AMQP service?",
         "OPTION_LIST": ["y", "n"],
         "VALIDATORS": [validators.validate_options],
         "DEFAULT_VALUE": "n",
         "MASK_INPUT": False,
         "LOOSE_VALIDATION": False,
         "CONF_NAME": "CONFIG_AMQP_ENABLE_AUTH",
         "USE_DEFAULT": False,
         "NEED_CONFIRM": False,
         "CONDITION": False},
    ]
    group = {"GROUP_NAME": "AMQP",
             "DESCRIPTION": "AMQP Config parameters",
             "PRE_CONDITION": False,
             "PRE_CONDITION_MATCH": True,
             "POST_CONDITION": False,
             "POST_CONDITION_MATCH": True}
    controller.addGroup(group, params)

    params = [
        {"CMD_OPTION": "amqp-nss-certdb-pw",
         "USAGE": ("The password for the NSS certificate database of the AMQP "
                   "service"),
         "PROMPT": "Enter the password for NSS certificate database",
         "OPTION_LIST": [],
         "VALIDATORS": [validators.validate_not_empty],
         "DEFAULT_VALUE": "PW_PLACEHOLDER",
         "PROCESSORS": [processors.process_password],
         "MASK_INPUT": True,
         "LOOSE_VALIDATION": True,
         "CONF_NAME": "CONFIG_AMQP_NSS_CERTDB_PW",
         "USE_DEFAULT": False,
         "NEED_CONFIRM": True,
         "CONDITION": False},

        {"CMD_OPTION": "amqp-ssl-port",
         "USAGE": ("The port in which the AMQP service listens to SSL "
                   "connections"),
         "PROMPT": "Enter the SSL port for the AMQP service",
         "OPTION_LIST": [],
         "VALIDATORS": [validators.validate_not_empty],
         "DEFAULT_VALUE": "5671",
         "MASK_INPUT": False,
         "LOOSE_VALIDATION": True,
         "CONF_NAME": "CONFIG_AMQP_SSL_PORT",
         "USE_DEFAULT": False,
         "NEED_CONFIRM": False,
         "CONDITION": False},

        {"CMD_OPTION": "amqp-ssl-cert-file",
         "USAGE": ("The filename of the certificate that the AMQP service "
                   "is going to use"),
         "PROMPT": ("Enter the filename of the SSL certificate for the AMQP "
                    "service"),
         "OPTION_LIST": [],
         "VALIDATORS": [validators.validate_not_empty],
         "DEFAULT_VALUE": "/etc/pki/tls/certs/amqp_selfcert.pem",
         "MASK_INPUT": False,
         "LOOSE_VALIDATION": True,
         "CONF_NAME": "CONFIG_AMQP_SSL_CERT_FILE",
         "USE_DEFAULT": False,
         "NEED_CONFIRM": False,
         "CONDITION": False},

        {"CMD_OPTION": "amqp-ssl-key-file",
         "USAGE": ("The filename of the private key that the AMQP service "
                   "is going to use"),
         "PROMPT": "Enter the private key filename",
         "OPTION_LIST": [],
         "VALIDATORS": [validators.validate_not_empty],
         "DEFAULT_VALUE": "/etc/pki/tls/private/amqp_selfkey.pem",
         "MASK_INPUT": False,
         "LOOSE_VALIDATION": True,
         "CONF_NAME": "CONFIG_AMQP_SSL_KEY_FILE",
         "USE_DEFAULT": False,
         "NEED_CONFIRM": False,
         "CONDITION": False},

        {"CMD_OPTION": "amqp-ssl-self-signed",
         "USAGE": "Auto Generates self signed SSL certificate and key",
         "PROMPT": "Generate Self Signed SSL Certificate",
         "OPTION_LIST": ["y", "n"],
         "VALIDATORS": [validators.validate_not_empty],
         "DEFAULT_VALUE": "y",
         "MASK_INPUT": False,
         "LOOSE_VALIDATION": True,
         "CONF_NAME": "CONFIG_AMQP_SSL_SELF_SIGNED",
         "USE_DEFAULT": False,
         "NEED_CONFIRM": False,
         "CONDITION": False},
    ]
    group = {"GROUP_NAME": "AMQPSSL",
             "DESCRIPTION": "AMQP Config SSL parameters",
             "PRE_CONDITION": "CONFIG_AMQP_ENABLE_SSL",
             "PRE_CONDITION_MATCH": "y",
             "POST_CONDITION": False,
             "POST_CONDITION_MATCH": True}
    controller.addGroup(group, params)

    params = [
        {"CMD_OPTION": "amqp-auth-user",
         "USAGE": "User for amqp authentication",
         "PROMPT": "Enter the user for amqp authentication",
         "OPTION_LIST": [],
         "VALIDATORS": [validators.validate_not_empty],
         "DEFAULT_VALUE": "amqp_user",
         "MASK_INPUT": False,
         "LOOSE_VALIDATION": True,
         "CONF_NAME": "CONFIG_AMQP_AUTH_USER",
         "USE_DEFAULT": False,
         "NEED_CONFIRM": False,
         "CONDITION": False},

        {"CMD_OPTION": "amqp-auth-password",
         "USAGE": "Password for user authentication",
         "PROMPT": "Enter the password for user authentication",
         "OPTION_LIST": ["y", "n"],
         "VALIDATORS": [validators.validate_not_empty],
         "PROCESSORS": [processors.process_password],
         "DEFAULT_VALUE": "PW_PLACEHOLDER",
         "MASK_INPUT": True,
         "LOOSE_VALIDATION": True,
         "CONF_NAME": "CONFIG_AMQP_AUTH_PASSWORD",
         "USE_DEFAULT": False,
         "NEED_CONFIRM": True,
         "CONDITION": False},
    ]
    group = {"GROUP_NAME": "AMQPAUTH",
             "DESCRIPTION": "AMQP Config Athentication parameters",
             "PRE_CONDITION": "CONFIG_AMQP_ENABLE_AUTH",
             "PRE_CONDITION_MATCH": "y",
             "POST_CONDITION": False,
             "POST_CONDITION_MATCH": True}
    controller.addGroup(group, params)


def initSequences(controller):
    amqpsteps = [
        {'title': 'Adding AMQP manifest entries',
         'functions': [create_manifest]}
    ]
    controller.addSequence("Installing AMQP", [], [], amqpsteps)


# ------------------------ step functions -------------------------

def create_manifest(config, messages):
    server = utils.ScriptRunner(config['CONFIG_AMQP_HOST'])
    if config['CONFIG_AMQP_ENABLE_SSL'] == 'y':
        config['CONFIG_AMQP_ENABLE_SSL'] = True
        config['CONFIG_AMQP_PROTOCOL'] = 'ssl'
        config['CONFIG_AMQP_CLIENTS_PORT'] = "5671"
        if config['CONFIG_AMQP_SSL_SELF_SIGNED'] == 'y':
            server.append(
                "openssl req -batch -new -x509 -nodes -keyout %s "
                "-out %s -days 1095"
                % (config['CONFIG_AMQP_SSL_KEY_FILE'],
                   config['CONFIG_AMQP_SSL_CERT_FILE'])
            )
            server.execute()
    else:
        # Set default values
        config['CONFIG_AMQP_CLIENTS_PORT'] = "5672"
        config['CONFIG_AMQP_SSL_PORT'] = "5671"
        config['CONFIG_AMQP_SSL_CERT_FILE'] = ''
        config['CONFIG_AMQP_SSL_KEY_FILE'] = ''
        config['CONFIG_AMQP_NSS_CERTDB_PW'] = ''
        config['CONFIG_AMQP_ENABLE_SSL'] = False
        config['CONFIG_AMQP_PROTOCOL'] = 'tcp'

    if config['CONFIG_AMQP_ENABLE_AUTH'] == 'n':
        config['CONFIG_AMQP_AUTH_PASSWORD'] = 'guest'
        config['CONFIG_AMQP_AUTH_USER'] = 'guest'

    manifestfile = "%s_amqp.pp" % config['CONFIG_AMQP_HOST']
    manifestdata = getManifestTemplate('amqp.pp')

    fw_details = dict()
    # All hosts should be able to talk to amqp
    for host in filtered_hosts(config, exclude=False):
        key = "amqp_%s" % host
        fw_details.setdefault(key, {})
        fw_details[key]['host'] = "%s" % host
        fw_details[key]['service_name'] = "amqp"
        fw_details[key]['chain'] = "INPUT"
        fw_details[key]['ports'] = ['5671', '5672']
        fw_details[key]['proto'] = "tcp"
    config['FIREWALL_AMQP_RULES'] = fw_details

    manifestdata += createFirewallResources('FIREWALL_AMQP_RULES')
    appendManifestFile(manifestfile, manifestdata, 'pre')
