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
Installs and configures Nova
"""

import os
import socket

from packstack.installer import basedefs
from packstack.installer import exceptions
from packstack.installer import processors
from packstack.installer import utils
from packstack.installer import validators

from packstack.modules.common import filtered_hosts
from packstack.modules.documentation import update_params_usage
from packstack.modules.ospluginutils import deliver_ssl_file
from packstack.modules.ospluginutils import generate_ssl_cert

# ------------- Nova Packstack Plugin Initialization --------------

PLUGIN_NAME = "OS-Nova"
PLUGIN_NAME_COLORED = utils.color_text(PLUGIN_NAME, 'blue')


def initConfig(controller):
    nova_params = {
        "NOVA": [
            {"CMD_OPTION": 'nova-db-purge-enable',
             "PROMPT": (
                 "Enter y if cron job for removing soft deleted DB rows "
                 "should be created"
             ),
             "OPTION_LIST": ['y', 'n'],
             "VALIDATORS": [validators.validate_not_empty],
             "PROCESSORS": [processors.process_bool],
             "DEFAULT_VALUE": 'y',
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": 'CONFIG_NOVA_DB_PURGE_ENABLE',
             "USE_DEFAULT": False,
             "NEED_CONFIRM": True,
             "CONDITION": False},

            {"CMD_OPTION": "nova-db-passwd",
             "PROMPT": "Enter the password for the Nova DB access",
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_not_empty],
             "DEFAULT_VALUE": "PW_PLACEHOLDER",
             "PROCESSORS": [processors.process_password],
             "MASK_INPUT": True,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_NOVA_DB_PW",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": True,
             "CONDITION": False},

            {"CMD_OPTION": "nova-ks-passwd",
             "PROMPT": "Enter the password for the Nova Keystone access",
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_not_empty],
             "DEFAULT_VALUE": "PW_PLACEHOLDER",
             "PROCESSORS": [processors.process_password],
             "MASK_INPUT": True,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_NOVA_KS_PW",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": True,
             "CONDITION": False},

            {"CMD_OPTION": "nova-manage-flavors",
             "PROMPT": (
                 "Should Packstack manage default Nova flavors"
             ),
             "OPTION_LIST": ["y", "n"],
             "VALIDATORS": [validators.validate_options],
             "DEFAULT_VALUE": "y",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_NOVA_MANAGE_FLAVORS",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "novasched-cpu-allocation-ratio",
             "PROMPT": "Enter the CPU overcommitment ratio. Set to 1.0 to "
                       "disable CPU overcommitment",
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_float],
             "DEFAULT_VALUE": 16.0,
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME": "CONFIG_NOVA_SCHED_CPU_ALLOC_RATIO",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "novasched-ram-allocation-ratio",
             "PROMPT": ("Enter the RAM overcommitment ratio. Set to 1.0 to "
                        "disable RAM overcommitment"),
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_float],
             "DEFAULT_VALUE": 1.5,
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME": "CONFIG_NOVA_SCHED_RAM_ALLOC_RATIO",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "novacompute-migrate-protocol",
             "PROMPT": ("Enter protocol which will be used for instance "
                        "migration"),
             "OPTION_LIST": ['tcp', 'ssh'],
             "VALIDATORS": [validators.validate_options],
             "DEFAULT_VALUE": 'ssh',
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME": "CONFIG_NOVA_COMPUTE_MIGRATE_PROTOCOL",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "nova-ssl-cert",
             "PROMPT": ("Enter the path to a PEM encoded certificate to be used "
                        "on the https server, leave blank if one should be "
                        "generated, this certificate should not require "
                        "a passphrase"),
             "OPTION_LIST": [],
             "VALIDATORS": [],
             "DEFAULT_VALUE": '',
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME": "CONFIG_VNC_SSL_CERT",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "nova-ssl-key",
             "PROMPT": ("Enter the SSL keyfile corresponding to the certificate "
                        "if one was entered"),
             "OPTION_LIST": [],
             "VALIDATORS": [],
             "DEFAULT_VALUE": "",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME": "CONFIG_VNC_SSL_KEY",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "nova-pci-alias",
             "PROMPT": ("Enter the PCI passthrough array of hash in JSON style for controller eg. "
                        "[{'vendor_id':'1234', 'product_id':'5678', "
                        "'name':'default'}, {...}] "),
             "OPTION_LIST": [],
             "VALIDATORS": [],
             "DEFAULT_VALUE": "",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME": "CONFIG_NOVA_PCI_ALIAS",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "nova-pci-passthrough-whitelist",
             "PROMPT": ("Enter the PCI passthrough whitelist as array of hash in JSON style for "
                        "controller eg. "
                        "[{'vendor_id':'1234', 'product_id':'5678', "
                        "'name':'default'}, {...}]"),
             "OPTION_LIST": [],
             "VALIDATORS": [],
             "DEFAULT_VALUE": "",
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": True,
             "CONF_NAME": "CONFIG_NOVA_PCI_PASSTHROUGH_WHITELIST",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": False,
             "CONDITION": False},

            {"CMD_OPTION": "nova-libvirt-virt-type",
             "PROMPT": (
                 "The nova hypervisor that should be used. Either qemu or kvm."
             ),
             "OPTION_LIST": ['qemu', 'kvm'],
             "DEFAULT_VALUE": '%{::default_hypervisor}',
             "MASK_INPUT": False,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_NOVA_LIBVIRT_VIRT_TYPE",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": True,
             "CONDITION": False},
        ],
    }
    update_params_usage(basedefs.PACKSTACK_DOC, nova_params)

    nova_groups = [
        {"GROUP_NAME": "NOVA",
         "DESCRIPTION": "Nova Options",
         "PRE_CONDITION": "CONFIG_NOVA_INSTALL",
         "PRE_CONDITION_MATCH": "y",
         "POST_CONDITION": False,
         "POST_CONDITION_MATCH": True},
    ]
    for group in nova_groups:
        params = nova_params[group["GROUP_NAME"]]
        controller.addGroup(group, params)


def initSequences(controller):
    if controller.CONF['CONFIG_NOVA_INSTALL'] != 'y':
        return

    novaapisteps = [
        {'title': 'Preparing Nova API entries',
         'functions': [create_api_manifest]},
        {'title': 'Creating ssh keys for Nova migration',
         'functions': [create_ssh_keys]},
        {'title': 'Gathering ssh host keys for Nova migration',
         'functions': [gather_host_keys]},
        {'title': 'Preparing Nova Compute entries',
         'functions': [create_compute_manifest]},
        {'title': 'Preparing Nova Scheduler entries',
         'functions': [create_sched_manifest]},
        {'title': 'Preparing Nova VNC Proxy entries',
         'functions': [create_vncproxy_manifest]},
        {'title': 'Preparing OpenStack Network-related Nova entries',
         'functions': [create_neutron_manifest]},
        {'title': 'Preparing Nova Common entries',
         'functions': [create_common_manifest]},
    ]

    controller.addSequence("Installing OpenStack Nova API", [], [],
                           novaapisteps)


# ------------------------ Step Functions -------------------------

def create_ssh_keys(config, messages):
    migration_key = os.path.join(basedefs.VAR_DIR, 'nova_migration_key')
    # Generate key if it does not exist
    if not os.path.exists(migration_key):
        local = utils.ScriptRunner()
        local.append('ssh-keygen -t rsa -b 2048 -f "%s" -N ""' % migration_key)
        local.execute()

    with open(migration_key) as fp:
        secret = fp.read().strip()
    with open('%s.pub' % migration_key) as fp:
        public = fp.read().strip()

    config['NOVA_MIGRATION_KEY_TYPE'] = 'ssh-rsa'
    config['NOVA_MIGRATION_KEY_PUBLIC'] = public.split()[1]
    config['NOVA_MIGRATION_KEY_SECRET'] = secret + '\n'


def gather_host_keys(config, messages):
    global compute_hosts

    for host in compute_hosts:
        local = utils.ScriptRunner()
        local.append('ssh-keyscan %s' % host)
        retcode, hostkey = local.execute()
        config['HOST_KEYS_%s' % host] = hostkey


def create_api_manifest(config, messages):
    # Since this step is running first, let's create necessary variables here
    # and make them global
    global compute_hosts, network_hosts
    com_var = config.get("CONFIG_COMPUTE_HOSTS", "")
    compute_hosts = set([i.strip() for i in com_var.split(",") if i.strip()])
    net_var = config.get("CONFIG_NETWORK_HOSTS", "")
    network_hosts = set([i.strip() for i in net_var.split(",") if i.strip()])

    # This is a hack around us needing to generate the neutron metadata
    # password, but the nova puppet plugin uses the existence of that
    # password to determine whether or not to configure neutron metadata
    # proxy support. So the nova_api.pp template needs to be set to None
    # to disable metadata support if neutron is not being installed.
    if config['CONFIG_NEUTRON_INSTALL'] != 'y':
        config['CONFIG_NEUTRON_METADATA_PW_UNQUOTED'] = None
    else:
        config['CONFIG_NEUTRON_METADATA_PW_UNQUOTED'] = "%s" % config['CONFIG_NEUTRON_METADATA_PW']

    fw_details = dict()
    key = "nova_api"
    fw_details.setdefault(key, {})
    fw_details[key]['host'] = "ALL"
    fw_details[key]['service_name'] = "nova api"
    fw_details[key]['chain'] = "INPUT"
    fw_details[key]['ports'] = ['8773', '8774', '8775', '8778']
    fw_details[key]['proto'] = "tcp"
    config['FIREWALL_NOVA_API_RULES'] = fw_details


def create_compute_manifest(config, messages):
    global compute_hosts, network_hosts

    if config["CONFIG_HORIZON_SSL"] == 'y':
        config["CONFIG_VNCPROXY_PROTOCOL"] = "https"
    else:
        config["CONFIG_VNCPROXY_PROTOCOL"] = "http"

    config["CONFIG_NOVA_ALLOW_RESIZE_TO_SAME"] = len(compute_hosts) == 1

    ssh_keys_details = {}
    for host in compute_hosts:
        try:
            hostname, aliases, addrs = socket.gethostbyaddr(host)
        except socket.herror:
            hostname, aliases, addrs = (host, [], [])

        for hostkey in config['HOST_KEYS_%s' % host].split('\n'):
            hostkey = hostkey.strip()
            if not hostkey:
                continue

            _, host_key_type, host_key_data = hostkey.split()
            key = "%s.%s" % (host_key_type, hostname)
            ssh_keys_details.setdefault(key, {})
            ssh_keys_details[key]['ensure'] = 'present'
            ssh_keys_details[key]['host_aliases'] = [hostname] + aliases + addrs
            ssh_keys_details[key]['key'] = host_key_data
            ssh_keys_details[key]['type'] = host_key_type

    config['SSH_KEYS'] = ssh_keys_details

    if config['CONFIG_VMWARE_BACKEND'] == 'y':
        vcenters = [i.strip() for i in
                    config['CONFIG_VCENTER_CLUSTER_NAMES'].split(',')
                    if i.strip()]
        if not vcenters:
            raise exceptions.ParamValidationError(
                "Please specify at least one VMware vCenter cluster in"
                " CONFIG_VCENTER_CLUSTER_NAMES"
            )
        if len(vcenters) != len(compute_hosts):
            if len(vcenters) > 1:
                raise exceptions.ParamValidationError(
                    "Number of vmware clusters %s is not same"
                    " as number of nova computes %s", (vcenters, compute_hosts)
                )
            else:
                vcenters = len(compute_hosts) * [vcenters[0]]
        vmware_clusters = dict(zip(compute_hosts, vcenters))
        config['CONFIG_VCENTER_CLUSTERS'] = vmware_clusters

    for host in compute_hosts:
        fw_details = dict()
        cf_fw_qemu_mig_key = ("FIREWALL_NOVA_QEMU_MIG_RULES_%s" %
                              host.replace('.', '_'))
        for c_host in compute_hosts:
            key = "nova_qemu_migration_%s_%s" % (host, c_host)
            fw_details.setdefault(key, {})
            fw_details[key]['host'] = "%s" % c_host
            fw_details[key]['service_name'] = "nova qemu migration"
            fw_details[key]['chain'] = "INPUT"
            fw_details[key]['ports'] = ['16509', '49152-49215']
            fw_details[key]['proto'] = "tcp"

        config[cf_fw_qemu_mig_key] = fw_details

        if config['CONFIG_CEILOMETER_INSTALL'] == 'y':
            if config['CONFIG_AMQP_ENABLE_SSL'] == 'y':
                ssl_cert_file = config['CONFIG_CEILOMETER_SSL_CERT'] = (
                    '/etc/pki/tls/certs/ssl_amqp_ceilometer.crt'
                )
                ssl_key_file = config['CONFIG_CEILOMETER_SSL_KEY'] = (
                    '/etc/pki/tls/private/ssl_amqp_ceilometer.key'
                )
                ssl_host = config['CONFIG_CONTROLLER_HOST']
                service = 'ceilometer'
                generate_ssl_cert(config, ssl_host, service, ssl_key_file,
                                  ssl_cert_file)

        fw_details = dict()
        key = "nova_compute"
        fw_details.setdefault(key, {})
        fw_details[key]['host'] = "%s" % config['CONFIG_CONTROLLER_HOST']
        fw_details[key]['service_name'] = "nova compute"
        fw_details[key]['chain'] = "INPUT"
        fw_details[key]['ports'] = ['5900-5999']
        fw_details[key]['proto'] = "tcp"
        config['FIREWALL_NOVA_COMPUTE_RULES'] = fw_details


def create_sched_manifest(config, messages):
    if config['CONFIG_IRONIC_INSTALL'] == 'y':
        ram_alloc = '1.0'
        config['CONFIG_NOVA_SCHED_RAM_ALLOC_RATIO'] = ram_alloc


def create_vncproxy_manifest(config, messages):
    if config["CONFIG_HORIZON_SSL"] == 'y':
        if config["CONFIG_VNC_SSL_CERT"]:
            ssl_cert_file = config["CONFIG_VNC_SSL_CERT"]
            ssl_key_file = config["CONFIG_VNC_SSL_KEY"]
            if not os.path.exists(ssl_cert_file):
                raise exceptions.ParamValidationError(
                    "The file %s doesn't exist" % ssl_cert_file)

            if not os.path.exists(ssl_key_file):
                raise exceptions.ParamValidationError(
                    "The file %s doesn't exist" % ssl_key_file)

            final_cert = open(ssl_cert_file, 'rt').read()
            final_key = open(ssl_key_file, 'rt').read()
            deliver_ssl_file(final_cert, ssl_cert_file, config['CONFIG_CONTROLLER_HOST'])
            deliver_ssl_file(final_key, ssl_key_file, config['CONFIG_CONTROLLER_HOST'])

        else:
            config["CONFIG_VNC_SSL_CERT"] = '/etc/pki/tls/certs/ssl_vnc.crt'
            config["CONFIG_VNC_SSL_KEY"] = '/etc/pki/tls/private/ssl_vnc.key'
            ssl_key_file = config["CONFIG_VNC_SSL_KEY"]
            ssl_cert_file = config["CONFIG_VNC_SSL_CERT"]
            ssl_host = config['CONFIG_CONTROLLER_HOST']
            service = 'vnc'
            generate_ssl_cert(config, ssl_host, service, ssl_key_file,
                              ssl_cert_file)


def create_common_manifest(config, messages):
    global compute_hosts, network_hosts

    dbacces_hosts = set([config.get('CONFIG_CONTROLLER_HOST')])
    dbacces_hosts |= network_hosts

    for host in filtered_hosts(config):
        pw_in_sqlconn = False
        host = host.strip()

        if host in compute_hosts and host not in dbacces_hosts:
            # we should omit password in case we are installing only
            # nova-compute to the host
            perms = "nova"
            pw_in_sqlconn = False
        else:
            perms = "nova:%s" % config['CONFIG_NOVA_DB_PW']
            pw_in_sqlconn = True

        mariadb_host_url = config['CONFIG_MARIADB_HOST_URL']
        sqlconn = "mysql+pymysql://%s@%s/nova" % (perms, mariadb_host_url)
        if pw_in_sqlconn:
            config['CONFIG_NOVA_SQL_CONN_PW'] = sqlconn
        else:
            config['CONFIG_NOVA_SQL_CONN_NOPW'] = sqlconn

        config['CONFIG_NOVA_METADATA_HOST'] = config['CONFIG_CONTROLLER_HOST']

    if config['CONFIG_AMQP_ENABLE_SSL'] == 'y':
        nova_hosts = compute_hosts
        nova_hosts |= set([config.get('CONFIG_CONTROLLER_HOST')])
        ssl_cert_file = config['CONFIG_NOVA_SSL_CERT'] = (
            '/etc/pki/tls/certs/ssl_amqp_nova.crt'
        )
        ssl_key_file = config['CONFIG_NOVA_SSL_KEY'] = (
            '/etc/pki/tls/private/ssl_amqp_nova.key'
        )
        service = 'nova'
        for host in nova_hosts:
            generate_ssl_cert(config, host, service,
                              ssl_key_file, ssl_cert_file)


def create_neutron_manifest(config, messages):
    if config['CONFIG_IRONIC_INSTALL'] == 'y':
        virt_driver = 'nova.virt.firewall.NoopFirewallDriver'
        config['CONFIG_NOVA_LIBVIRT_VIF_DRIVER'] = virt_driver
    else:
        virt_driver = 'nova.virt.libvirt.vif.LibvirtGenericVIFDriver'
        config['CONFIG_NOVA_LIBVIRT_VIF_DRIVER'] = virt_driver
