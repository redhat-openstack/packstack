# -*- coding: utf-8 -*-
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

"""
Plugin responsible for managing SSL options
"""
import os

from OpenSSL import crypto
from socket import gethostname

from packstack.installer import basedefs
from packstack.installer import utils
from packstack.installer import validators

from packstack.modules.documentation import update_params_usage

# ------------- SSL Packstack Plugin Initialization --------------

PLUGIN_NAME = "SSL"
PLUGIN_NAME_COLORED = utils.color_text(PLUGIN_NAME, 'blue')


def initConfig(controller):
    params = {
        "SSL": [
            {"CMD_OPTION": "ssl-cacert-file",
             "PROMPT": ("Enter the filename of the SSL CAcertificate, if the"
                        " CONFIG_SSL_CACERT_SELFSIGN is set to y the path "
                        "will be CONFIG_SSL_CERT_DIR/certs/selfcert.crt"),
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_not_empty],
             "DEFAULT_VALUE": "/etc/pki/tls/certs/selfcert.crt",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME": "CONFIG_SSL_CACERT_FILE",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "ssl-cacert-key-file",
             "PROMPT": ("Enter the filename of the SSL CAcertificate Key file"
                        ", if the CONFIG_SSL_CACERT_SELFSIGN is set to y the "
                        "path will be CONFIG_SSL_CERT_DIR/keys/selfkey.key"),
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_not_empty],
             "DEFAULT_VALUE": "/etc/pki/tls/private/selfkey.key",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME": "CONFIG_SSL_CACERT_KEY_FILE",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "ssl-cert-dir",
             "PROMPT": ("Enter the path to use to store generated SSL certificates in"),
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_not_empty,
                            validators.validate_writeable_directory],
             "DEFAULT_VALUE": "~/packstackca/",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME": "CONFIG_SSL_CERT_DIR",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "ssl-cacert-selfsign",
             "PROMPT": "Should packstack use selfsigned CAcert.",
             "OPTION_LIST": ["y", "n"],
             "VALIDATORS": [validators.validate_options],
             "DEFAULT_VALUE": "y",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": 'CONFIG_SSL_CACERT_SELFSIGN',
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "ssl-cert-subject-country",
             "PROMPT": "Enter the ssl certificates subject country.",
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_not_empty],
             "DEFAULT_VALUE": "--",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": 'CONFIG_SSL_CERT_SUBJECT_C',
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False,
             "DEPRECATES": ['CONFIG_SELFSIGN_CACERT_SUBJECT_C']},

            {"CMD_OPTION": "ssl-cert-subject-state",
             "PROMPT": "Enter the ssl certificates subject state.",
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_not_empty],
             "DEFAULT_VALUE": "State",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": 'CONFIG_SSL_CERT_SUBJECT_ST',
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False,
             "DEPRECATES": ['CONFIG_SELFSIGN_CACERT_SUBJECT_ST']},

            {"CMD_OPTION": "ssl-cert-subject-location",
             "PROMPT": "Enter the ssl certificate subject location.",
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_not_empty],
             "DEFAULT_VALUE": "City",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": 'CONFIG_SSL_CERT_SUBJECT_L',
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False,
             "DEPRECATES": ['CONFIG_SELFSIGN_CACERT_SUBJECT_L']},

            {"CMD_OPTION": "ssl-cert-subject-organization",
             "PROMPT": "Enter the ssl certificate subject organization.",
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_not_empty],
             "DEFAULT_VALUE": "openstack",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": 'CONFIG_SSL_CERT_SUBJECT_O',
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False,
             "DEPRECATES": ['CONFIG_SELFSIGN_CACERT_SUBJECT_O']},

            {"CMD_OPTION": "ssl-cert-subject-organizational-unit",
             "PROMPT": "Enter the ssl certificate subject organizational unit.",
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_not_empty],
             "DEFAULT_VALUE": "packstack",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": 'CONFIG_SSL_CERT_SUBJECT_OU',
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False,
             "DEPRECATES": ['CONFIG_SELFSIGN_CACERT_SUBJECT_OU']},

            {"CMD_OPTION": "ssl-cert-subject-common-name",
             "PROMPT": "Enter the ssl certificaate subject common name.",
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_not_empty],
             "DEFAULT_VALUE": gethostname(),
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": 'CONFIG_SSL_CERT_SUBJECT_CN',
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False,
             "DEPRECATES": ['CONFIG_SELFSIGN_CACERT_SUBJECT_CN']},

            {"CMD_OPTION": "ssl-cert-subject-email",
             "PROMPT": "Enter the ssl certificate subject admin email.",
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_not_empty],
             "DEFAULT_VALUE": "admin@%s" % gethostname(),
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": 'CONFIG_SSL_CERT_SUBJECT_MAIL',
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False,
             "DEPRECATES": ['CONFIG_SELFSIGN_CACERT_SUBJECT_MAIL']},
        ]
    }
    update_params_usage(basedefs.PACKSTACK_DOC, params)

    groups = [
        {"GROUP_NAME": "SSL",
         "DESCRIPTION": "SSL Config parameters",
         "PRE_CONDITION": lambda x: 'yes',
         "PRE_CONDITION_MATCH": "yes",
         "POST_CONDITION": False,
         "POST_CONDITION_MATCH": True},
    ]
    for group in groups:
        controller.addGroup(group, params[group['GROUP_NAME']])


def initSequences(controller):
    ssl_steps = [
        {'title': 'Setting up CACERT',
         'functions': [create_self_signed_cert]}
    ]
    controller.addSequence("Setting up SSL", [], [],
                           ssl_steps)


# ------------------------- helper functions -------------------------

def create_self_signed_cert(config, messages):
    """
    OpenSSL wrapper to create selfsigned CA.
    """

    # for now hardcoded place for landing CACert file on servers
    config['CONFIG_SSL_CACERT'] = '/etc/pki/tls/certs/packstack_cacert.crt'

    if (config['CONFIG_AMQP_ENABLE_SSL'] != 'y' and
       config["CONFIG_HORIZON_SSL"] != 'y'):
        return

    config['CONFIG_SSL_CERT_DIR'] = os.path.expanduser(
        config['CONFIG_SSL_CERT_DIR']
    )

    if not os.path.isdir(config['CONFIG_SSL_CERT_DIR']):
        os.mkdir(config['CONFIG_SSL_CERT_DIR'])
    certs = os.path.join(config['CONFIG_SSL_CERT_DIR'], 'certs')
    if not os.path.isdir(certs):
        os.mkdir(certs)
    keys = os.path.join(config['CONFIG_SSL_CERT_DIR'], 'keys')
    if not os.path.isdir(keys):
        os.mkdir(keys)

    if config['CONFIG_SSL_CACERT_SELFSIGN'] != 'y':
        return

    CERT_FILE = config['CONFIG_SSL_CACERT_FILE'] = (
        '%s/certs/selfcert.crt' % config['CONFIG_SSL_CERT_DIR']
    )
    KEY_FILE = config['CONFIG_SSL_CACERT_KEY_FILE'] = (
        '%s/keys/selfcert.crt' % config['CONFIG_SSL_CERT_DIR']
    )
    if not os.path.exists(CERT_FILE) or not os.path.exists(KEY_FILE):
        # create a key pair
        k = crypto.PKey()
        k.generate_key(crypto.TYPE_RSA, 4096)

        # create a self-signed cert
        mail = config['CONFIG_SSL_CERT_SUBJECT_MAIL']
        cert = crypto.X509()
        subject = cert.get_subject()
        subject.C = config['CONFIG_SSL_CERT_SUBJECT_C']
        subject.ST = config['CONFIG_SSL_CERT_SUBJECT_ST']
        subject.L = config['CONFIG_SSL_CERT_SUBJECT_L']
        subject.O = config['CONFIG_SSL_CERT_SUBJECT_O']
        subject.OU = config['CONFIG_SSL_CERT_SUBJECT_OU']
        subject.CN = config['CONFIG_SSL_CERT_SUBJECT_CN']
        subject.emailAddress = mail
        cert.set_serial_number(1000)
        cert.gmtime_adj_notBefore(0)
        cert.gmtime_adj_notAfter(10 * 365 * 24 * 60 * 60)
        cert.set_issuer(cert.get_subject())
        cert.set_pubkey(k)

        # CA extensions
        cert.add_extensions([
            crypto.X509Extension("basicConstraints".encode('ascii'), False,
                                 "CA:TRUE".encode('ascii')),
            crypto.X509Extension("keyUsage".encode('ascii'), False,
                                 "keyCertSign, cRLSign".encode('ascii')),
            crypto.X509Extension("subjectKeyIdentifier".encode('ascii'), False,
                                 "hash".encode('ascii'),
                                 subject=cert),
        ])

        cert.add_extensions([
            crypto.X509Extension(
                "authorityKeyIdentifier".encode('ascii'), False,
                "keyid:always".encode('ascii'), issuer=cert)
        ])

        cert.sign(k, 'sha1')

        open((CERT_FILE), "w").write(
            crypto.dump_certificate(crypto.FILETYPE_PEM, cert).decode())
        open((KEY_FILE), "w").write(
            crypto.dump_privatekey(crypto.FILETYPE_PEM, k).decode())

        messages.append(
            "%sNOTE%s : A selfsigned CA certificate was generated to be used "
            "for ssl, you should still change it do subordinate CA cert. In "
            "any case please save the contents of %s."
            % (utils.COLORS['red'], utils.COLORS['nocolor'],
                config['CONFIG_SSL_CERT_DIR']))
