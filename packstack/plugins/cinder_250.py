"""
Installs and configures Cinder
"""

import os
import uuid
import logging

from packstack.installer import exceptions
from packstack.installer import run_setup as setup
from packstack.installer import engine_validators as validate
from packstack.installer import engine_processors as process

from packstack.installer import basedefs
import packstack.installer.common_utils as utils
from packstack.installer.exceptions import InstallError

from packstack.modules.ospluginutils import getManifestTemplate, appendManifestFile

# Controller object will be initialized from main flow
controller = None

# Plugin name
PLUGIN_NAME = "OS-Cinder"
PLUGIN_NAME_COLORED = utils.getColoredText(PLUGIN_NAME, basedefs.BLUE)

logging.debug("plugin %s loaded", __name__)

def initConfig(controllerObject):
    global controller
    controller = controllerObject
    logging.debug("Adding OpenStack Cinder configuration")
    paramsList = [
                  {"CMD_OPTION"      : "cinder-host",
                   "USAGE"           : "The IP address of the server on which to install Cinder",
                   "PROMPT"          : "Enter the IP address of the Cinder server",
                   "OPTION_LIST"     : [],
                   "VALIDATORS"      : [validate.validate_ssh],
                   "DEFAULT_VALUE"   : utils.getLocalhostIP(),
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_CINDER_HOST",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "cinder-db-passwd",
                   "USAGE"           : "The password to use for the Cinder to access DB",
                   "PROMPT"          : "Enter the password for the Cinder DB access",
                   "OPTION_LIST"     : [],
                   "VALIDATORS"      : [validate.validate_not_empty],
                   "DEFAULT_VALUE"   : uuid.uuid4().hex[:16],
                   "MASK_INPUT"      : True,
                   "LOOSE_VALIDATION": False,
                   "CONF_NAME"       : "CONFIG_CINDER_DB_PW",
                   "USE_DEFAULT"     : True,
                   "NEED_CONFIRM"    : True,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "cinder-ks-passwd",
                   "USAGE"           : "The password to use for the Cinder to authenticate with Keystone",
                   "PROMPT"          : "Enter the password for the Cinder Keystone access",
                   "OPTION_LIST"     : [],
                   "VALIDATORS"      : [validate.validate_not_empty],
                   "DEFAULT_VALUE"   : uuid.uuid4().hex[:16],
                   "MASK_INPUT"      : True,
                   "LOOSE_VALIDATION": False,
                   "CONF_NAME"       : "CONFIG_CINDER_KS_PW",
                   "USE_DEFAULT"     : True,
                   "NEED_CONFIRM"    : True,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "cinder-volumes-size",
                   "USAGE"           : "Cinder's volumes group size",
                   "PROMPT"          : "Enter Cinder's volumes group size",
                   "OPTION_LIST"     : [],
                   "VALIDATION_FUNC" : validate.validateStringNotEmpty,
                   "DEFAULT_VALUE"   : "2G",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": False,
                   "CONF_NAME"       : "CONFIG_CINDER_VOLUMES_SIZE",
                   "USE_DEFAULT"     : True,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "cinder-volumes-path",
                   "USAGE"           : "Cinder's volumes group path",
                   "PROMPT"          : "Enter Cinder's volumes group path",
                   "OPTION_LIST"     : [],
                   "VALIDATION_FUNC" : validate.validateStringNotEmpty,
                   "DEFAULT_VALUE"   : "/var/lib/cinder",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": False,
                   "CONF_NAME"       : "CONFIG_CINDER_VOLUMES_PATH",
                   "USE_DEFAULT"     : True,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "cinder-volumes",
                   "USAGE"           : "Cinder's volumes group name",
                   "PROMPT"          : "Enter Cinder's volumes group name",
                   "OPTION_LIST"     : [],
                   "VALIDATION_FUNC" : validate.validateStringNotEmpty,
                   "DEFAULT_VALUE"   : "cinder-volumes",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": False,
                   "CONF_NAME"       : "CONFIG_CINDER_VOLUMES",
                   "USE_DEFAULT"     : True,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "cinder-volumes-create",
                   "USAGE"           : "Create Cinder's volumes group",
                   "PROMPT"          : "Should Cinder's volumes group be created?",
                   "OPTION_LIST"     : ["y", "n"],
                   "VALIDATION_FUNC" : createVolume,
                   "DEFAULT_VALUE"   : "y",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": False,
                   "CONF_NAME"       : "CONFIG_CINDER_VOLUMES_CREATE",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                 ]

    groupDict = { "GROUP_NAME"            : "CINDER",
                  "DESCRIPTION"           : "Cinder Config parameters",
                  "PRE_CONDITION"         : "CONFIG_CINDER_INSTALL",
                  "PRE_CONDITION_MATCH"   : "y",
                  "POST_CONDITION"        : False,
                  "POST_CONDITION_MATCH"  : True}

    controller.addGroup(groupDict, paramsList)


def initSequences(controller):
    if controller.CONF['CONFIG_CINDER_INSTALL'] != 'y':
        return

    cindersteps = [
             {'title': 'Adding Cinder Keystone manifest entries', 'functions':[createkeystonemanifest]},
             {'title': 'Checking if the Cinder server has a cinder-volumes vg', 'functions':[checkcindervg]},
             {'title': 'Adding Cinder manifest entries', 'functions':[createmanifest]}
    ]
    controller.addSequence("Installing OpenStack Cinder", [], [], cindersteps)



def createVolume(param, options=[]):
    """
    Check that provided host is listening on port 22
    """
    if param == "n":
        return True

    for option in ['CONFIG_CINDER_VOLUMES_SIZE', 'CONFIG_CINDER_VOLUMES_PATH']:
        param = controller.getParamByName(option)
        param.setKey('USE_DEFAULT', False)
        setup.input_param(param)
    return True


def checkcindervg():
    server = utils.ScriptRunner(controller.CONF['CONFIG_CINDER_HOST'])

    cinders_volume = controller.CONF['CONFIG_CINDER_VOLUMES']

    if controller.CONF["CONFIG_CINDER_VOLUMES_CREATE"] != "y":
        server.append('vgdisplay %s' % cinders_volume)
        err = "The cinder server should contain a cinder-volumes volume group"
    else:
        logging.info("A new cinder volumes group will be created")
        err = "Cinder's volume group '%s' could not be created" % \
                            controller.CONF['CONFIG_CINDER_VOLUMES']

        cinders_volume_path = controller.CONF['CONFIG_CINDER_VOLUMES_PATH']
        server.append('mkdir -p  %s' % cinders_volume_path)
        logging.debug("Volume's path: %s" % cinders_volume_path)

        cinders_volume_path = os.path.join(cinders_volume_path, cinders_volume)
        server.append('dd if=/dev/zero of=%s bs=1 count=0 seek=%s' % \
            (cinders_volume_path, controller.CONF['CONFIG_CINDER_VOLUMES_SIZE']))
        server.append('losetup /dev/loop2  %s' % cinders_volume_path)
        server.append('pvcreate /dev/loop2')
        server.append('vgcreate %s /dev/loop2' % cinders_volume)

        # Let's make sure it exists
        server.append('vgdisplay %s' % cinders_volume)

    try:
        server.execute()
    except:
        if controller.CONF["CONFIG_CINDER_VOLUMES_CREATE"] == "y":
            # Release loop device if cinder's volume creation
            # fails.
            try:
                logging.debug("Release loop device since volume's creation failed")
                server = utils.ScriptRunner(controller.CONF['CONFIG_CINDER_HOST'])
                server.append('losetup -d /dev/loop2')
                server.execute()
            except:
                pass

        raise exceptions.MissingRequirements(err)


def createkeystonemanifest():
    manifestfile = "%s_keystone.pp" % controller.CONF['CONFIG_KEYSTONE_HOST']
    manifestdata = getManifestTemplate("keystone_cinder.pp")
    appendManifestFile(manifestfile, manifestdata)


def createmanifest():
    manifestfile = "%s_cinder.pp" % controller.CONF['CONFIG_CINDER_HOST']
    manifestdata = getManifestTemplate("cinder.pp")
    appendManifestFile(manifestfile, manifestdata)
