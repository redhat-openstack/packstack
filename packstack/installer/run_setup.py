import ConfigParser
import copy
import datetime
import getpass
import logging
import os
import re
import sys
from StringIO import StringIO
import traceback
import types
import textwrap

from optparse import OptionParser, OptionGroup

import basedefs
import validators
from . import utils
import processors
import output_messages
from .exceptions import FlagValidationError, ParamValidationError

from packstack.modules.ospluginutils import gethostlist
from setup_controller import Controller

controller = Controller()
commandLineValues = {}

# List to hold all values to be masked in logging (i.e. passwords and sensitive data)
#TODO: read default values from conf_param?
masked_value_set = set()


def initLogging (debug):
    global logFile

    try:
        logFilename = "openstack-setup.log"
        logFile = os.path.join(basedefs.DIR_LOG, logFilename)

        # Create the log file with specific permissions, puppet has a habbit of putting
        # passwords in logs
        os.close(os.open(logFile, os.O_CREAT | os.O_EXCL, 0600))

        hdlr = logging.FileHandler (filename=logFile, mode='w')
        if (debug):
            level = logging.DEBUG
        else:
            level = logging.INFO

        fmts='%(asctime)s::%(levelname)s::%(module)s::%(lineno)d::%(name)s:: %(message)s'
        dfmt='%Y-%m-%d %H:%M:%S'
        fmt = logging.Formatter(fmts, dfmt)
        hdlr.setFormatter(fmt)

        logging.root.handlers = []
        logging.root.addHandler(hdlr)
        logging.root.setLevel(level)
    except:
        logging.error(traceback.format_exc())
        raise Exception(output_messages.ERR_EXP_FAILED_INIT_LOGGER)

def _getInputFromUser(param):
    """
    this private func reads the data from the user
    for the given param
    """
    loop = True
    userInput = None

    try:
        if param.USE_DEFAULT:
            logging.debug("setting default value (%s) for key (%s)" % (mask(param.DEFAULT_VALUE), param.CONF_NAME))
            controller.CONF[param.CONF_NAME] = param.DEFAULT_VALUE
        else:
            while loop:
                # If the value was not supplied by the command line flags
                if not commandLineValues.has_key(param.CONF_NAME):
                    message = StringIO()
                    message.write(param.PROMPT)

                    val_list = param.VALIDATORS or []
                    if validators.validate_regexp not in val_list \
                       and param.OPTION_LIST:
                        message.write(" [%s]" % "|".join(param.OPTION_LIST))

                    if param.DEFAULT_VALUE:
                        message.write("  [%s] " % (str(param.DEFAULT_VALUE)))

                    message.write(": ")
                    message.seek(0)
                    #mask password or hidden fields

                    if (param.MASK_INPUT):
                        userInput = getpass.getpass("%s :" % (param.PROMPT))
                    else:
                        userInput = raw_input(message.read())
                else:
                    userInput = commandLineValues[param.CONF_NAME]
                # If DEFAULT_VALUE is set and user did not input anything
                if userInput == "" and len(str(param.DEFAULT_VALUE)) > 0:
                    userInput = param.DEFAULT_VALUE

                # Param processing
                userInput = process_param_value(param, userInput)

                # If param requires validation
                try:
                    validate_param_value(param, userInput)
                    controller.CONF[param.CONF_NAME] = userInput
                    loop = False
                except ParamValidationError:
                    if param.LOOSE_VALIDATION:
                        # If validation failed but LOOSE_VALIDATION is true, ask user
                        answer = _askYesNo("User input failed validation, "
                                           "do you still wish to use it")
                        loop = not answer
                        if answer:
                            controller.CONF[param.CONF_NAME] = userInput
                            continue
                        else:
                            if commandLineValues.has_key(param.CONF_NAME):
                                del commandLineValues[param.CONF_NAME]
                    else:
                        # Delete value from commandLineValues so that we will prompt the user for input
                        if commandLineValues.has_key(param.CONF_NAME):
                            del commandLineValues[param.CONF_NAME]
                        loop = True
    except KeyboardInterrupt:
        print "" # add the new line so messages wont be displayed in the same line as the question
        raise
    except:
        logging.error(traceback.format_exc())
        raise Exception(output_messages.ERR_EXP_READ_INPUT_PARAM % (param.CONF_NAME))

def input_param(param):
    """
    this func will read input from user
    and ask confirmation if needed
    """
    # We need to check if a param needs confirmation, (i.e. ask user twice)
    # Do not validate if it was given from the command line
    if (param.NEED_CONFIRM and not commandLineValues.has_key(param.CONF_NAME)):
        #create a copy of the param so we can call it twice
        confirmedParam = copy.deepcopy(param)
        confirmedParamName = param.CONF_NAME + "_CONFIRMED"
        confirmedParam.CONF_NAME = confirmedParamName
        confirmedParam.PROMPT = output_messages.INFO_CONF_PARAMS_PASSWD_CONFIRM_PROMPT
        confirmedParam.VALIDATORS = [validators.validate_not_empty]
        # Now get both values from user (with existing validations
        while True:
            _getInputFromUser(param)
            _getInputFromUser(confirmedParam)
            if controller.CONF[param.CONF_NAME] == controller.CONF[confirmedParamName]:
                logging.debug("Param confirmation passed, value for both questions is identical")
                break
            else:
                print output_messages.INFO_VAL_PASSWORD_DONT_MATCH
    else:
        _getInputFromUser(param)

    return param

def _askYesNo(question=None):
    message = StringIO()

    while True:
        askString = "\r%s? (yes|no): "%(question)
        logging.debug("asking user: %s"%askString)

        message.write(askString)
        message.seek(0)

        raw = raw_input(message.read())
        if not len(raw):
            continue

        answer = raw[0].lower()
        logging.debug("user answered read: %s"%(answer))

        if answer not in 'yn':
            continue

        return answer == 'y'

def _addDefaultsToMaskedValueSet():
    """
    For every param in conf_params
    that has MASK_INPUT enabled keep the default value
    in the 'masked_value_set'
    """
    global masked_value_set
    for group in controller.getAllGroups():
        for param in group.parameters.itervalues():
            # Keep default password values masked, but ignore default empty values
            if ((param.MASK_INPUT == True) and param.DEFAULT_VALUE != ""):
                masked_value_set.add(param.DEFAULT_VALUE)

def _updateMaskedValueSet():
    """
    For every param in conf
    has MASK_INPUT enabled keep the user input
    in the 'masked_value_set'
    """
    global masked_value_set
    for confName in controller.CONF:
        # Add all needed values to masked_value_set
        if (controller.getParamKeyValue(confName, "MASK_INPUT") == True):
            masked_value_set.add(controller.CONF[confName])

def mask(input):
    """
    Gets a dict/list/str and search maksked values in them.
    The list of masked values in is masked_value_set and is updated
    via the user input
    If it finds, it replaces them with '********'
    """
    output = copy.deepcopy(input)
    if type(input) == types.DictType:
        for key in input:
            if type(input[key]) == types.StringType:
                output[key] = utils.mask_string(input[key],
                                                masked_value_set)
    if type(input) == types.ListType:
        for item in input:
            org = item
            orgIndex = input.index(org)
            if type(item) == types.StringType:
                item = utils.mask_string(item, masked_value_set)
            if item != org:
                output.remove(org)
                output.insert(orgIndex, item)
    if type(input) == types.StringType:
            output = utils.mask_string(input, masked_value_set)

    return output

def removeMaskString(maskedString):
    """
    remove an element from masked_value_set
    we need to itterate over the set since
    calling set.remove() on an string that does not exit
    will raise an exception
    """
    global masked_value_set
    # Since we cannot remove an item from a set during itteration over
    # the said set, we only mark a flag and if the flag is set to True
    # we remove the string from the set.
    found = False
    for item in masked_value_set:
        if item == maskedString:
            found = True
    if found:
        masked_value_set.remove(maskedString)

def validate_param_value(param, value):
    cname = param.CONF_NAME
    logging.debug("Validating parameter %s." % cname)

    val_list = param.VALIDATORS or []
    opt_list = param.OPTION_LIST
    for val_func in val_list:
        try:
            val_func(value, opt_list)
        except ParamValidationError as ex:
            print 'Parameter %s failed validation: %s' % (cname, ex)
            raise

def process_param_value(param, value):
    _value = value
    proclist = param.PROCESSORS or []
    for proc_func in proclist:
        logging.debug("Processing value of parameter "
                      "%s." % param.CONF_NAME)
        try:
            new_value = proc_func(_value, controller.CONF)
            if new_value != _value:
                msg = output_messages.INFO_CHANGED_VALUE
                print msg % (_value, new_value)
                _value = new_value
            else:
                logging.debug("Processor returned the original "
                              "value: %s" % _value)
        except processors.ParamProcessingError, ex:
            print ("Value processing of parameter %s "
                   "failed.\n%s" % (param.CONF_NAME, ex))
            raise
    return _value

def _handleGroupCondition(config, conditionName, conditionValue):
    """
    handle params group pre/post condition
    checks if a group has a pre/post condition
    and validates the params related to the group
    """

    # If the post condition is a function
    if callable(conditionName):
        # Call the function conditionName with conf as the arg
        conditionValue = conditionName(controller.CONF)

    # If the condition is a string - just read it to global conf
    # We assume that if we get a string as a member it is the name of a member of conf_params
    elif type(conditionName) == types.StringType:
        conditionValue = _loadParamFromFile(config, "general", conditionName)
    else:
        # Any other type is invalid
        raise TypeError("%s type (%s) is not supported" % (conditionName, type(conditionName)))
    return conditionValue


def _loadParamFromFile(config, section, paramName):
    """
    read param from file
    validate it
    and load to to global conf dict
    """

    # Get paramName from answer file
    try:
        value = config.get(section, paramName)
    except ConfigParser.NoOptionError:
        raise KeyError('Parser cannot find option %s in '
                       'answer file.' % paramName)

    # Validate param value using its validation func
    param = controller.getParamByName(paramName)
    value = process_param_value(param, value)
    validate_param_value(param, value)

    # Keep param value in our never ending global conf
    controller.CONF[param.CONF_NAME] = value

    return value

def _handleAnswerFileParams(answerFile):
    """
    handle loading and validating
    params from answer file
    supports reading single or group params
    """
    try:
        logging.debug("Starting to handle config file")

        # Read answer file
        fconf = ConfigParser.ConfigParser()
        fconf.read(answerFile)

        # Iterate all the groups and check the pre/post conditions
        for group in controller.getAllGroups():
            # Get all params per group

            # Handle pre conditions for group
            preConditionValue = True
            if group.PRE_CONDITION:
                preConditionValue = _handleGroupCondition(fconf, group.PRE_CONDITION, preConditionValue)

            # Handle pre condition match with case insensitive values
            logging.info("Comparing pre- conditions, value: '%s', and match: '%s'" % (preConditionValue, group.PRE_CONDITION_MATCH))
            if preConditionValue == group.PRE_CONDITION_MATCH:
                for param in group.parameters.itervalues():
                    _loadParamFromFile(fconf, "general", param.CONF_NAME)

                # Handle post conditions for group only if pre condition passed
                postConditionValue = True
                if group.POST_CONDITION:
                    postConditionValue = _handleGroupCondition(fconf, group.POST_CONDITION, postConditionValue)

                    # Handle post condition match for group
                    if postConditionValue != group.POST_CONDITION_MATCH:
                        logging.error("The group condition (%s) returned: %s, which differs from the excpeted output: %s"%\
                                      (group.GROUP_NAME, postConditionValue, group.POST_CONDITION_MATCH))
                        raise ValueError(output_messages.ERR_EXP_GROUP_VALIDATION_ANS_FILE%\
                                         (group.GROUP_NAME, postConditionValue, group.POST_CONDITION_MATCH))
                    else:
                        logging.debug("condition (%s) passed" % group.POST_CONDITION)
                else:
                    logging.debug("no post condition check for group %s" % group.GROUP_NAME)
            else:
                logging.debug("skipping params group %s since value of group validation is %s" % (group.GROUP_NAME, preConditionValue))

    except Exception as e:
        logging.error(traceback.format_exc())
        raise Exception(output_messages.ERR_EXP_HANDLE_ANSWER_FILE%(e))


def _getanswerfilepath():
    path = None
    msg = "Could not find a suitable path on which to create the answerfile"

    ts = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')

    p = os.path.expanduser("~/")
    if os.access(p, os.W_OK):
        path = os.path.abspath(os.path.join(p, "packstack-answers-%s.txt"%ts))
        msg = "A new answerfile was created in: %s" % path

    controller.MESSAGES.append(msg)
    logging.info(msg)
    return path

def _handleInteractiveParams():
    try:
        logging.debug("Groups: %s" % ', '.join([x.GROUP_NAME for x in controller.getAllGroups()]))

        for group in controller.getAllGroups():
            preConditionValue = True
            logging.debug("going over group %s" % group.GROUP_NAME)

            # If pre_condition is set, get Value
            if group.PRE_CONDITION:
                preConditionValue = _getConditionValue(group.PRE_CONDITION)

            inputLoop = True

            # If we have a match, i.e. condition returned True, go over all params in the group
            logging.info("Comparing pre-conditions; condition: '%s', and match: '%s'" % (preConditionValue, group.PRE_CONDITION_MATCH))
            if preConditionValue == group.PRE_CONDITION_MATCH:
                while inputLoop:
                    for param in group.parameters.itervalues():
                        if not param.CONDITION:
                            input_param(param)
                            #update password list, so we know to mask them
                            _updateMaskedValueSet()

                    postConditionValue = True

                    # If group has a post condition, we check it after we get the input from
                    # all the params in the group. if the condition returns False, we loop over the group again
                    if group.POST_CONDITION:
                        postConditionValue = _getConditionValue(group.POST_CONDITION)

                        if postConditionValue == group.POST_CONDITION_MATCH:
                            inputLoop = False
                        else:
                            #we clear the value of all params in the group
                            #in order to re-input them by the user
                            for param in group.parameters.itervalues():
                                if controller.CONF.has_key(param.CONF_NAME):
                                    del controller.CONF[param.CONF_NAME]
                                if commandLineValues.has_key(param.CONF_NAME):
                                    del commandLineValues[param.CONF_NAME]
                    else:
                        inputLoop = False
            else:
                logging.debug("no post condition check for group %s" % group.GROUP_NAME)

        path = _getanswerfilepath()

        _displaySummary()

        if path:
            generateAnswerFile(path)

    except KeyboardInterrupt:
        logging.error("keyboard interrupt caught")
        raise Exception(output_messages.ERR_EXP_KEYBOARD_INTERRUPT)
    except Exception:
        logging.error(traceback.format_exc())
        raise
    except:
        logging.error(traceback.format_exc())
        raise Exception(output_messages.ERR_EXP_HANDLE_PARAMS)

def _handleParams(configFile):
    _addDefaultsToMaskedValueSet()
    if configFile:
        _handleAnswerFileParams(configFile)
    else:
        _handleInteractiveParams()

def _getConditionValue(matchMember):
    returnValue = False
    if type(matchMember) == types.FunctionType:
        returnValue = matchMember(controller.CONF)
    elif type(matchMember) == types.StringType:
        #we assume that if we get a string as a member it is the name
        #of a member of conf_params
        if not controller.CONF.has_key(matchMember):
            param = controller.getParamByName(matchMember)
            input_param(param)
        returnValue = controller.CONF[matchMember]
    else:
        raise TypeError("%s type (%s) is not supported"%(matchMember, type(matchMember)))

    return returnValue

def _displaySummary():

    print output_messages.INFO_DSPLY_PARAMS
    print  "=" * (len(output_messages.INFO_DSPLY_PARAMS) - 1)
    logging.info("*** User input summary ***")
    for group in controller.getAllGroups():
        for param in group.parameters.itervalues():
            if not param.USE_DEFAULT and controller.CONF.has_key(param.CONF_NAME):
                cmdOption = param.CMD_OPTION
                l = 30 - len(cmdOption)
                maskParam = param.MASK_INPUT
                # Only call mask on a value if the param has MASK_INPUT set to True
                if maskParam:
                    logging.info("%s: %s" % (cmdOption, mask(controller.CONF[param.CONF_NAME])))
                    print "%s:" % (cmdOption) + " " * l + mask(controller.CONF[param.CONF_NAME])
                else:
                    # Otherwise, log & display it as it is
                    logging.info("%s: %s" % (cmdOption, str(controller.CONF[param.CONF_NAME])))
                    print "%s:" % (cmdOption) + " " * l + str(controller.CONF[param.CONF_NAME])
    logging.info("*** User input summary ***")
    answer = _askYesNo(output_messages.INFO_USE_PARAMS)
    if not answer:
        logging.debug("user chose to re-enter the user parameters")
        for group in controller.getAllGroups():
            for param in group.parameters.itervalues():
                if controller.CONF.has_key(param.CONF_NAME):
                    if not param.MASK_INPUT:
                        param.DEFAULT_VALUE = controller.CONF[param.CONF_NAME]
                    # Remove the string from mask_value_set in order
                    # to remove values that might be over overwritten.
                    removeMaskString(controller.CONF[param.CONF_NAME])
                    del controller.CONF[param.CONF_NAME]
                if commandLineValues.has_key(param.CONF_NAME):
                    del commandLineValues[param.CONF_NAME]
            print ""
        logging.debug("calling handleParams in interactive mode")
        return _handleParams(None)
    else:
        logging.debug("user chose to accept user parameters")

def _printAdditionalMessages():
    if len(controller.MESSAGES) > 0:
        print "\n",output_messages.INFO_ADDTIONAL_MSG
    for msg in controller.MESSAGES:
        logging.info(output_messages.INFO_ADDTIONAL_MSG_BULLET%(msg))
        print output_messages.INFO_ADDTIONAL_MSG_BULLET%(msg)

def _addFinalInfoMsg():
    """
    add info msg to the user finalizing the
    successfull install of rhemv
    """
    controller.MESSAGES.append(output_messages.INFO_LOG_FILE_PATH%(logFile))


def _summaryParamsToLog():
    if len(controller.CONF) > 0:
        logging.debug("*** The following params were used as user input:")
        for group in controller.getAllGroups():
            for param in group.parameters.itervalues():
                if controller.CONF.has_key(param.CONF_NAME):
                    maskedValue = mask(controller.CONF[param.CONF_NAME])
                    logging.debug("%s: %s" % (param.CMD_OPTION, maskedValue ))


def runSequences():
    controller.runAllSequences()

def _main(configFile=None):
    logging.debug("Entered main(configFile='%s')"%(configFile))
    print output_messages.INFO_HEADER

    # Get parameters
    _handleParams(configFile)

    # Update masked_value_list with user input values
    _updateMaskedValueSet()

    # Print masked conf
    logging.debug(mask(controller.CONF))

    # Start configuration stage
    logging.debug("Entered Configuration stage")
    print "\n",output_messages.INFO_INSTALL

    # Initialize Sequences
    initPluginsSequences()

    # Run main setup logic
    runSequences()

    # Lock rhevm version
    #_lockRpmVersion()

    # Print info
    _addFinalInfoMsg()
    print output_messages.INFO_INSTALL_SUCCESS


def remove_remote_var_dirs():
    """
    Removes the temp directories on remote hosts,
    doesn't remove data on localhost
    """
    for host in gethostlist(controller.CONF):
        try:
            host_dir = controller.temp_map[host]
        except KeyError:
            # Nothing was added to this host yet, so we have nothing to delete
            continue
        logging.info(output_messages.INFO_REMOVE_REMOTE_VAR % (host_dir, host))
        server = utils.ScriptRunner(host)
        server.append('rm -rf %s' % host_dir)
        try:
            server.execute()
        except Exception, e:
            msg = output_messages.ERR_REMOVE_REMOTE_VAR % (host_dir, host)
            logging.error(msg)
            logging.exception(e)
            controller.MESSAGES.append(utils.color_text(msg, 'red'))


def generateAnswerFile(outputFile, overrides={}):
    sep = os.linesep
    fmt = ("%(comment)s%(separator)s%(conf_name)s=%(default_value)s"
           "%(separator)s")

    outputFile = os.path.expanduser(outputFile)
    # Remove the answer file so it can be recreated as the current user with
    # the mode -rw-------
    if os.path.exists(outputFile):
        os.remove(outputFile)
    fd = os.open(outputFile, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0600)

    with os.fdopen(fd, "w") as ans_file:
        ans_file.write("[general]%s" % os.linesep)
        for group in controller.getAllGroups():
            for param in group.parameters.itervalues():
                comm = param.USAGE or ''
                comm = textwrap.fill(comm,
                                     initial_indent='%s# ' % sep,
                                     subsequent_indent='# ',
                                     break_long_words=False)
                value = controller.CONF.get(param.CONF_NAME,
                                            param.DEFAULT_VALUE)

                args = {'comment': comm,
                        'separator': sep,
                        'default_value': overrides.get(param.CONF_NAME, value),
                        'conf_name': param.CONF_NAME}
                ans_file.write(fmt % args)

def single_step_aio_install(options):
    """ Installs an All in One host on this host"""

    options.install_hosts = utils.get_localhost_ip()

    # Also allow the command line to set values for any of these options
    # by testing if they have been set before we set them here
    if not options.os_swift_install:
        options.os_swift_install = "y"
    if not options.nagios_install:
        options.nagios_install = "y"
    if not options.novanetwork_pubif:
        options.novanetwork_pubif = utils.device_from_ip(options.install_hosts)
    if not options.novacompute_privif:
        options.novacompute_privif = "lo"
    if not options.novanetwork_privif:
        options.novanetwork_privif = "lo"

    # If we are doing an all-in-one install and neutron isn't disabled
    # go ahead and set up a basic network and external bridge unless
    # specifically told not to
    if options.os_neutron_install != "n":
        if not options.provision_demo:
            options.provision_demo = "y"
        if not options.provision_all_in_one_ovs_bridge:
            options.provision_all_in_one_ovs_bridge = "y"

    single_step_install(options)

def single_step_install(options):
    answerfilepath =  _getanswerfilepath()
    if not answerfilepath:
        _printAdditionalMessages()
        return

    # We're going to generate the answerfile and run Packstack in a single step
    # todo this we generate the answerfile and pass in some override variables to
    # override the default hosts
    overrides = {}

    hosts = options.install_hosts
    hosts = [host.strip() for host in hosts.split(',')]
    for group in controller.getAllGroups():
        for param in group.parameters.itervalues():
            # and directives that contain _HOST are set to the controller node
            if param.CONF_NAME.find("_HOST") != -1:
                overrides[param.CONF_NAME] = hosts[0]
    # If there are more than one host, all but the first are a compute nodes
    if len(hosts) > 1:
        overrides["CONFIG_NOVA_COMPUTE_HOSTS"] = ','.join(hosts[1:])

    # We can also override defaults with command line options
    _set_command_line_values(options)
    for key,value in commandLineValues.items():
        overrides[key] = value

    generateAnswerFile(answerfilepath, overrides)
    _main(answerfilepath)

def initCmdLineParser():
    """
    Initiate the optparse object, add all the groups and general command line flags
    and returns the optparse object
    """

    # Init parser and all general flags
    logging.debug("initiating command line option parser")
    usage = "usage: %prog [options] [--help]"
    parser = OptionParser(usage)
    parser.add_option("--gen-answer-file", help="Generate a template of an answer file, using this option excludes all other options")
    parser.add_option("--answer-file", help="Runs the configuration in non-interactive mode, extracting all information from the \
                                            configuration file. using this option excludes all other options")
    parser.add_option("--install-hosts", help="Install on a set of hosts in a single step. The format should be a comma separated list "
                                          "of hosts, the first is setup as a controller, and the others are setup as compute nodes."
                                          "if only a single host is supplied then it is setup as an all in one installation. An answerfile "
                                          "will also be generated and should be used if Packstack needs to be run a second time ")
    parser.add_option("--allinone", action="store_true", help="Shorthand for --install-hosts=<local ipaddr> --novanetwork-pubif=<dev> "
                                          "--novacompute-privif=lo --novanetwork-privif=lo --os-swift-install=y --nagios-install=y "
                                          ", this option can be used to install an all in one OpenStack on this host")

    parser.add_option("-o", "--options", action="store_true", dest="options", help="Print details on options available in answer file(rst format)")
    parser.add_option("-d", "--debug", action="store_true", default=False, help="Enable debug in logging")

    # For each group, create a group option
    for group in controller.getAllGroups():
        groupParser = OptionGroup(parser, group.DESCRIPTION)

        for param in group.parameters.itervalues():
            cmdOption = param.CMD_OPTION
            paramUsage = param.USAGE
            optionsList = param.OPTION_LIST
            useDefault = param.USE_DEFAULT

            if not useDefault:
                groupParser.add_option("--%s" % cmdOption, help=paramUsage)

        # Add group parser to main parser
        parser.add_option_group(groupParser)

    return parser

def printOptions():
    """
    print and document the available options to the answer file (rst format)
    """

    # For each group, create a group option
    for group in controller.getAllGroups():
        print "%s" % group.DESCRIPTION
        print "-" * len(group.DESCRIPTION)
        print

        for param in group.parameters.itervalues():
            cmdOption = param.CONF_NAME
            paramUsage = param.USAGE
            optionsList = param.OPTION_LIST or ""
            print "%s : %s %s"%(("**%s**"%str(cmdOption)).ljust(30), paramUsage, optionsList)
            print

def plugin_compare(x, y):
    """
    Used to sort the plugin file list
    according to the number at the end of the plugin module
    """
    x_match = re.search(".+\_(\d\d\d)", x)
    x_cmp = x_match.group(1)
    y_match = re.search(".+\_(\d\d\d)", y)
    y_cmp = y_match.group(1)
    return int(x_cmp) - int(y_cmp)

def loadPlugins():
    """
    Load All plugins from ./plugins
    """
    sys.path.append(basedefs.DIR_PLUGINS)
    sys.path.append(basedefs.DIR_MODULES)

    fileList = [f for f in os.listdir(basedefs.DIR_PLUGINS) if f[0] != "_"]
    fileList = sorted(fileList, cmp=plugin_compare)
    for item in fileList:
        # Looking for files that end with ###.py, example: a_plugin_100.py
        match = re.search("^(.+\_\d\d\d)\.py$", item)
        if match:
            try:
                moduleToLoad = match.group(1)
                logging.debug("importing module %s, from file %s", moduleToLoad, item)
                moduleobj = __import__(moduleToLoad)
                moduleobj.__file__ = os.path.join(basedefs.DIR_PLUGINS, item)
                globals()[moduleToLoad] = moduleobj
                checkPlugin(moduleobj)
                controller.addPlugin(moduleobj)
            except:
                 logging.error("Failed to load plugin from file %s", item)
                 logging.error(traceback.format_exc())
                 raise Exception("Failed to load plugin from file %s" % item)

def checkPlugin(plugin):
    for funcName in ['initConfig','initSequences']:
        if not hasattr(plugin, funcName):
            raise ImportError("Plugin %s does not contain the %s function" % (plugin.__class__, funcName))


def countCmdLineFlags(options, flag):
    """
    counts all command line flags that were supplied, excluding the supplied flag name
    """
    counter = 0
    # make sure only flag was supplied
    for key, value  in options.__dict__.items():
        if key == flag:
            next
        # Do not count --debug
        elif key == 'debug':
            next
        # If anything but flag was called, increment
        elif value:
            counter += 1

    return counter


def validateSingleFlag(options, flag):
    counter = countCmdLineFlags(options, flag)
    if counter > 0:
        flag = flag.replace("_","-")
        msg = output_messages.ERR_ONLY_1_FLAG % ("--%s" % flag)
        raise FlagValidationError(msg)

def setProvisioningDefaults():
    pnames = ['CONFIG_PROVISION_' + x for x in ['DEMO', 'TEMPEST', 'ALL_IN_ONE_OVS_BRIDGE']]
    params = [controller.getParamByName(x) for x in pnames]
    for param in params:
        controller.CONF[param.CONF_NAME] = (
            controller.CONF.get(param.CONF_NAME, param.DEFAULT_VALUE)
        )

def initPluginsConfig():
    for plugin in controller.getAllPlugins():
        plugin.initConfig(controller)

def initPluginsSequences():
    setProvisioningDefaults()
    for plugin in controller.getAllPlugins():
        plugin.initSequences(controller)

def _set_command_line_values(options):
    for key, value in options.__dict__.items():
        # Replace the _ with - in the string since optparse replace _ with -
        for group in controller.getAllGroups():
            param = group.search("CMD_OPTION", key.replace("_","-"))
            if len(param) > 0 and value:
                commandLineValues[param[0].CONF_NAME] = value

def main():
    try:
        # Load Plugins
        loadPlugins()
        initPluginsConfig()

        optParser = initCmdLineParser()

        # Do the actual command line parsing
        # Try/Except are here to catch the silly sys.exit(0) when calling rhevm-setup --help
        (options, args) = optParser.parse_args()

        if options.options:
            printOptions()
            raise SystemExit

        # Initialize logging
        initLogging (options.debug)

        # Parse parameters
        runConfiguration = True
        confFile = None

        # If --gen-answer-file was supplied, do not run main
        if options.gen_answer_file:
            # Make sure only --gen-answer-file was supplied
            validateSingleFlag(options, "gen_answer_file")
            generateAnswerFile(options.gen_answer_file)
        # Are we installing an all in one
        elif options.allinone:
            if getattr(options, 'answer_file', None):
                msg = ('Please use either --allinone or --answer-file, '
                       'but not both.')
                raise FlagValidationError(msg)
            single_step_aio_install(options)
        # Are we installing in a single step
        elif options.install_hosts:
            single_step_install(options)
        # Otherwise, run main()
        else:
            # Make sure only --answer-file was supplied
            if options.answer_file:
                validateSingleFlag(options, "answer_file")
                confFile = os.path.expanduser(options.answer_file)
                if not os.path.exists(confFile):
                    raise Exception(output_messages.ERR_NO_ANSWER_FILE % confFile)
            else:
                _set_command_line_values(options)
            _main(confFile)

    except FlagValidationError, ex:
        optParser.error(str(ex))
    except Exception as e:
        logging.error(traceback.format_exc())
        print
        print utils.color_text("ERROR : " + str(e), 'red')
        print output_messages.ERR_CHECK_LOG_FILE_FOR_MORE_INFO%(logFile)
        sys.exit(1)

    finally:
        remove_remote_var_dirs()

        # Always print user params to log
        _printAdditionalMessages()
        _summaryParamsToLog()


if __name__ == "__main__":
    main()
