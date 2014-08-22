# -*- coding: utf-8 -*-

"""
Installs and configures Cinder
"""

import os
import re
import uuid
import logging

from packstack.installer import exceptions
from packstack.installer import processors
from packstack.installer import validators
from packstack.installer.utils import split_hosts

from packstack.installer import basedefs
from packstack.installer import utils


from packstack.modules.shortcuts import get_mq
from packstack.modules.ospluginutils import (getManifestTemplate,
                                             appendManifestFile)

from packstack.installer import exceptions
from packstack.installer import output_messages


#------------------ oVirt installer initialization ------------------

PLUGIN_NAME = "OS-Cinder"
PLUGIN_NAME_COLORED = utils.color_text(PLUGIN_NAME, 'blue')


def initConfig(controller):
    params = [
        {"CMD_OPTION": "cinder-db-passwd",
         "USAGE": "The password to use for the Cinder to access DB",
         "PROMPT": "Enter the password for the Cinder DB access",
         "OPTION_LIST": [],
         "VALIDATORS": [validators.validate_not_empty],
         "DEFAULT_VALUE": uuid.uuid4().hex[:16],
         "MASK_INPUT": True,
         "LOOSE_VALIDATION": False,
         "CONF_NAME": "CONFIG_CINDER_DB_PW",
         "USE_DEFAULT": True,
         "NEED_CONFIRM": True,
         "CONDITION": False},

        {"CMD_OPTION": "cinder-ks-passwd",
         "USAGE": ("The password to use for the Cinder to authenticate with "
                   "Keystone"),
         "PROMPT": "Enter the password for the Cinder Keystone access",
         "OPTION_LIST": [],
         "VALIDATORS": [validators.validate_not_empty],
         "DEFAULT_VALUE": uuid.uuid4().hex[:16],
         "MASK_INPUT": True,
         "LOOSE_VALIDATION": False,
         "CONF_NAME": "CONFIG_CINDER_KS_PW",
         "USE_DEFAULT": True,
         "NEED_CONFIRM": True,
         "CONDITION": False},

        {"CMD_OPTION": "cinder-backend",
         "USAGE": ("The Cinder backend to use, valid options are: lvm, "
                   "gluster, nfs"),
         "PROMPT": "Enter the Cinder backend to be configured",
         "OPTION_LIST": ["lvm", "gluster", "nfs", "vmdk"],
         "VALIDATORS": [validators.validate_options],
         "DEFAULT_VALUE": "lvm",
         "MASK_INPUT": False,
         "LOOSE_VALIDATION": False,
         "CONF_NAME": "CONFIG_CINDER_BACKEND",
         "USE_DEFAULT": False,
         "NEED_CONFIRM": False,
         "CONDITION": False},
    ]
    group = {"GROUP_NAME": "CINDER",
             "DESCRIPTION": "Cinder Config parameters",
             "PRE_CONDITION": "CONFIG_CINDER_INSTALL",
             "PRE_CONDITION_MATCH": "y",
             "POST_CONDITION": False,
             "POST_CONDITION_MATCH": True}
    controller.addGroup(group, params)

    def check_lvm_options(config):
        return (config.get('CONFIG_CINDER_INSTALL', 'n') == 'y' and
                config.get('CONFIG_CINDER_BACKEND', 'lvm') == 'lvm')

    params = [
        {"CMD_OPTION": "cinder-volumes-create",
         "USAGE": ("Create Cinder's volumes group. This should only be done "
                   "for testing on a proof-of-concept installation of Cinder. "
                   "This will create a file-backed volume group and is not "
                   "suitable for production usage."),
         "PROMPT": ("Should Cinder's volumes group be created (for "
                    "proof-of-concept installation)?"),
         "OPTION_LIST": ["y", "n"],
         "VALIDATORS": [validators.validate_options],
         "DEFAULT_VALUE": "y",
         "MASK_INPUT": False,
         "LOOSE_VALIDATION": False,
         "CONF_NAME": "CONFIG_CINDER_VOLUMES_CREATE",
         "USE_DEFAULT": False,
         "NEED_CONFIRM": False,
         "CONDITION": False},
    ]
    group = {"GROUP_NAME": "CINDERVOLUMECREATE",
             "DESCRIPTION": "Cinder volume create Config parameters",
             "PRE_CONDITION": check_lvm_options,
             "PRE_CONDITION_MATCH": True,
             "POST_CONDITION": False,
             "POST_CONDITION_MATCH": True}
    controller.addGroup(group, params)

    def check_lvm_vg_options(config):
        return (config.get('CONFIG_CINDER_INSTALL', 'n') == 'y' and
                config.get('CONFIG_CINDER_BACKEND', 'lvm') == 'lvm' and
                config.get('CONFIG_CINDER_VOLUMES_CREATE', 'y') == 'y')

    params = [
        {"CMD_OPTION": "cinder-volumes-size",
         "USAGE": ("Cinder's volumes group size. Note that actual volume size "
                   "will be extended with 3% more space for VG metadata."),
         "PROMPT": "Enter Cinder's volumes group usable size",
         "OPTION_LIST": [],
         "VALIDATORS": [validators.validate_not_empty],
         "DEFAULT_VALUE": "20G",
         "MASK_INPUT": False,
         "LOOSE_VALIDATION": False,
         "CONF_NAME": "CONFIG_CINDER_VOLUMES_SIZE",
         "USE_DEFAULT": False,
         "NEED_CONFIRM": False,
         "CONDITION": False},
    ]
    group = {"GROUP_NAME": "CINDERVOLUMESIZE",
             "DESCRIPTION": "Cinder volume size Config parameters",
             "PRE_CONDITION": check_lvm_vg_options,
             "PRE_CONDITION_MATCH": True,
             "POST_CONDITION": False,
             "POST_CONDITION_MATCH": True}
    controller.addGroup(group, params)

    def check_gluster_options(config):
        return (config.get('CONFIG_CINDER_INSTALL', 'n') == 'y' and
                config.get('CONFIG_CINDER_BACKEND', 'lvm') == 'gluster')

    params = [
        {"CMD_OPTION": "cinder-gluster-mounts",
         "USAGE": ("A single or comma separated list of gluster volume shares "
                   "to mount, eg: ip-address:/vol-name, domain:/vol-name "),
         "PROMPT": ("Enter a single or comma separated list of gluster volume "
                    "shares to use with Cinder"),
         "OPTION_LIST": ["^'([\d]{1,3}\.){3}[\d]{1,3}:/.*'",
                         "^'[a-zA-Z0-9][\-\.\w]*:/.*'"],
         "VALIDATORS": [validators.validate_multi_regexp],
         "PROCESSORS": [processors.process_add_quotes_around_values],
         "DEFAULT_VALUE": "",
         "MASK_INPUT": False,
         "LOOSE_VALIDATION": True,
         "CONF_NAME": "CONFIG_CINDER_GLUSTER_MOUNTS",
         "USE_DEFAULT": False,
         "NEED_CONFIRM": False,
         "CONDITION": False},
    ]
    group = {"GROUP_NAME": "CINDERGLUSTERMOUNTS",
             "DESCRIPTION": "Cinder gluster Config parameters",
             "PRE_CONDITION": check_gluster_options,
             "PRE_CONDITION_MATCH": True,
             "POST_CONDITION": False,
             "POST_CONDITION_MATCH": True}
    controller.addGroup(group, params)

    def check_nfs_options(config):
        return (config.get('CONFIG_CINDER_INSTALL', 'n') == 'y' and
                config.get('CONFIG_CINDER_BACKEND', 'lvm') == 'nfs')

    params = [
        {"CMD_OPTION": "cinder-nfs-mounts",
         "USAGE": ("A single or comma seprated list of NFS exports to mount, "
                   "eg: ip-address:/export-name "),
         "PROMPT": ("Enter a single or comma seprated list of NFS exports to "
                    "use with Cinder"),
         "OPTION_LIST": ["^'([\d]{1,3}\.){3}[\d]{1,3}:/.*'"],
         "VALIDATORS": [validators.validate_multi_regexp],
         "PROCESSORS": [processors.process_add_quotes_around_values],
         "DEFAULT_VALUE": "",
         "MASK_INPUT": False,
         "LOOSE_VALIDATION": True,
         "CONF_NAME": "CONFIG_CINDER_NFS_MOUNTS",
         "USE_DEFAULT": False,
         "NEED_CONFIRM": False,
         "CONDITION": False},
    ]
    group = {"GROUP_NAME": "CINDERNFSMOUNTS",
             "DESCRIPTION": "Cinder NFS Config parameters",
             "PRE_CONDITION": check_nfs_options,
             "PRE_CONDITION_MATCH": True,
             "POST_CONDITION": False,
             "POST_CONDITION_MATCH": True}
    controller.addGroup(group, params)


def initSequences(controller):
    if controller.CONF['CONFIG_CINDER_INSTALL'] != 'y':
        return

    cinder_steps = [
        {'title': 'Adding Cinder Keystone manifest entries',
         'functions': [create_keystone_manifest]},
        {'title': 'Adding Cinder manifest entries',
         'functions': [create_manifest]}
    ]

    if controller.CONF['CONFIG_CINDER_BACKEND'] == 'lvm':
        cinder_steps.append(
            {'title': 'Checking if the Cinder server has a cinder-volumes vg',
             'functions': [check_cinder_vg]})
    controller.addSequence("Installing OpenStack Cinder", [], [], cinder_steps)


#-------------------------- step functions --------------------------

def check_cinder_vg(config, messages):
    cinders_volume = 'cinder-volumes'
    if config['CONFIG_UNSUPPORTED'] != 'y':
        config['CONFIG_STORAGE_HOST'] = config['CONFIG_CONTROLLER_HOST']

    # Do we have a cinder-volumes vg?
    have_cinders_volume = False
    server = utils.ScriptRunner(config['CONFIG_STORAGE_HOST'])
    server.append('vgdisplay %s' % cinders_volume)
    try:
        server.execute()
        have_cinders_volume = True
    except exceptions.ScriptRuntimeError:
        pass

    # Configure system LVM settings (snapshot_autoextend)
    server = utils.ScriptRunner(config['CONFIG_STORAGE_HOST'])
    server.append('sed -i -r "s/^ *snapshot_autoextend_threshold +=.*/'
                  '    snapshot_autoextend_threshold = 80/" '
                  '/etc/lvm/lvm.conf')
    server.append('sed -i -r "s/^ *snapshot_autoextend_percent +=.*/'
                  '    snapshot_autoextend_percent = 20/" '
                  '/etc/lvm/lvm.conf')
    try:
        server.execute()
    except exceptions.ScriptRuntimeError:
        logging.info("Warning: Unable to set system LVM settings.")

    if config["CONFIG_CINDER_VOLUMES_CREATE"] != "y":
        if not have_cinders_volume:
            raise exceptions.MissingRequirements("The cinder server should "
                                                 "contain a cinder-volumes "
                                                 "volume group")
    else:
        if have_cinders_volume:
            messages.append(
                output_messages.INFO_CINDER_VOLUMES_EXISTS)
            return

        # TO-DO: This is implemented in cinder::setup_test_volume class.
        #        We should use it instead of this Python code
        server = utils.ScriptRunner(config['CONFIG_STORAGE_HOST'])
        server.append('systemctl')
        try:
            server.execute()
            rst_cmd = 'systemctl restart openstack-cinder-volume.service'
        except exceptions.ScriptRuntimeError:
            rst_cmd = 'service openstack-cinder-volume restart'

        server.clear()
        logging.info("A new cinder volumes group will be created")
        server.append('yum install -y lvm2')

        cinders_volume_path = '/var/lib/cinder'
        server.append('mkdir -p  %s' % cinders_volume_path)
        logging.debug("Volume's path: %s" % cinders_volume_path)

        match = re.match('^(?P<size>\d+)G$',
                         config['CONFIG_CINDER_VOLUMES_SIZE'].strip())
        if not match:
            msg = 'Invalid Cinder volumes VG size.'
            raise exceptions.ParamValidationError(msg)

        cinders_volume_size = int(match.group('size')) * 1024
        cinders_reserve = int(cinders_volume_size * 0.03)

        cinders_volume_size = cinders_volume_size + cinders_reserve
        cinders_volume_path = os.path.join(cinders_volume_path, cinders_volume)
        server.append('dd if=/dev/zero of=%s bs=1 count=0 seek=%sM'
                      % (cinders_volume_path, cinders_volume_size))
        server.append('LOFI=$(losetup --show -f  %s)' % cinders_volume_path)
        server.append('pvcreate $LOFI')
        server.append('vgcreate %s $LOFI' % cinders_volume)

        # Add the loop device on boot
        server.append('grep %(volume)s /etc/rc.d/rc.local || '
                      'echo "losetup -f %(path)s && '
                      'vgchange -a y %(volume)s && '
                      '%(restart_cmd)s" '
                      '>> /etc/rc.d/rc.local' %
                      {'volume': cinders_volume, 'restart_cmd': rst_cmd,
                       'path': cinders_volume_path})
        server.append('grep "#!" /etc/rc.d/rc.local || '
                      'sed -i \'1i#!/bin/sh\' /etc/rc.d/rc.local')
        server.append('chmod +x /etc/rc.d/rc.local')

        # Let's make sure it exists
        server.append('vgdisplay %s' % cinders_volume)

        try:
            server.execute()
        except exceptions.ScriptRuntimeError:
            # Release loop device if cinder's volume creation
            # fails.
            try:
                logging.debug("Release loop device, volume creation failed")
                server = utils.ScriptRunner(config['CONFIG_STORAGE_HOST'])
                server.append('losetup -d $(losetup -j %s | cut -d : -f 1)'
                              % cinders_volume_path)
                server.execute()
            except:
                pass

            raise exceptions.MissingRequirements("Cinder's volume group '%s' "
                                                 "could not be created"
                                                 % cinders_volume)


def create_keystone_manifest(config, messages):
    if config['CONFIG_UNSUPPORTED'] != 'y':
        config['CONFIG_STORAGE_HOST'] = config['CONFIG_CONTROLLER_HOST']

    manifestfile = "%s_keystone.pp" % config['CONFIG_CONTROLLER_HOST']
    manifestdata = getManifestTemplate("keystone_cinder.pp")
    appendManifestFile(manifestfile, manifestdata)


def create_manifest(config, messages):
    if config['CONFIG_UNSUPPORTED'] != 'y':
        config['CONFIG_STORAGE_HOST'] = config['CONFIG_CONTROLLER_HOST']

    manifestdata = getManifestTemplate(get_mq(config, "cinder"))
    manifestfile = "%s_cinder.pp" % config['CONFIG_STORAGE_HOST']
    manifestdata += getManifestTemplate("cinder.pp")

    if config['CONFIG_CINDER_BACKEND'] == "lvm":
        manifestdata += getManifestTemplate("cinder_lvm.pp")
    elif config['CONFIG_CINDER_BACKEND'] == "gluster":
        manifestdata += getManifestTemplate("cinder_gluster.pp")
    elif config['CONFIG_CINDER_BACKEND'] == "nfs":
        manifestdata += getManifestTemplate("cinder_nfs.pp")
    elif config['CONFIG_CINDER_BACKEND'] == "vmdk":
        manifestdata += getManifestTemplate("cinder_vmdk.pp")
    if config['CONFIG_CEILOMETER_INSTALL'] == 'y':
        manifestdata += getManifestTemplate('cinder_ceilometer.pp')
    if config['CONFIG_SWIFT_INSTALL'] == 'y':
        manifestdata += getManifestTemplate('cinder_backup.pp')

    config['FIREWALL_SERVICE_NAME'] = "cinder"
    config['FIREWALL_PORTS'] = "['3260', '8776']"
    config['FIREWALL_CHAIN'] = "INPUT"
    config['FIREWALL_PROTOCOL'] = 'tcp'
    if (config['CONFIG_NOVA_INSTALL'] == 'y' and
            config['CONFIG_VMWARE_BACKEND'] == 'n'):
        for host in split_hosts(config['CONFIG_COMPUTE_HOSTS']):
            config['FIREWALL_ALLOWED'] = "'%s'" % host
            config['FIREWALL_SERVICE_ID'] = "cinder_%s" % host
            manifestdata += getManifestTemplate("firewall.pp")
    else:
        config['FIREWALL_ALLOWED'] = "'ALL'"
        config['FIREWALL_SERVICE_ID'] = "cinder_ALL"
        manifestdata += getManifestTemplate("firewall.pp")

    appendManifestFile(manifestfile, manifestdata)
