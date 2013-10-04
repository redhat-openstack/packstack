"""
Controller class is a SINGLETON which handles all groups, params, sequences,
steps and replaces the CONF dictionary.
"""
from .core.parameters import Group
from .core.sequences import Sequence


def steps_new_format(steplist):
    # we have to duplicate title to name parameter and also only sigle
    # function is allowed in new step
    return [{'name': i['title'], 'title': i['title'],
             'function': i['functions'][0]} for i in steplist]


class Controller(object):

    __GROUPS=[]
    __SEQUENCES=[]
    __PLUGINS=[]
    MESSAGES=[]
    CONF={}

    __single = None # the one, true Singleton ... for god's sake why ??? :)

    def __new__(self, *args, **kwargs):
        """
        Singleton implementation.
        Will return __single if self is the same class as the class of __single
        which means that we will not invoke this singleton if someone tries to create a new
        instance from a class which inherit Controller.
        did not use isinstance because inheritence makes it behave erratically.
        """
        if self != type(self.__single):
            self.__single = object.__new__(self, *args, **kwargs)
        return self.__single

    def __init__(self):
        # Resources that should be copied to each host along with the puppet
        # files, on the remote host the file will be placed in
        # $PACKSTACK_VAR_DIR/resources. This controller should copy the files,
        # for now the puppet plugin is doing it format
        # {'host':[('/path/to/fileordirectory', 'filenameonremotehost'), ..]}
        self.resources = {}


    def addResource(self, host, localpath, remotename):
        """ Populates self.resources """
        current_value_for_host = self.resources.get(host, [])
        current_value_for_host.append((localpath,remotename))
        self.resources[host] = current_value_for_host


    # PLugins
    def addPlugin(self, plugObj):
        self.__PLUGINS.append(plugObj)

    def getPluginByName(self, pluginName):
        for plugin in self.__PLUGINS:
            if plugin.__name__ == pluginName:
                return plugin
        return None

    def getAllPlugins(self):
        return self.__PLUGINS

    # Sequences and steps
    def addSequence(self, desc, cond, cond_match, steps):
        self.__SEQUENCES.append(Sequence(desc, steps_new_format(steps),
                                         condition=cond,
                                         cond_match=cond_match))

    def insertSequence(self, desc, cond, cond_match, steps, index=0):
        self.__SEQUENCES.insert(index, Sequence(desc,
                                                steps_new_format(steps),
                                                condition=cond,
                                                cond_match=cond_match))

    def getAllSequences(self):
        return self.__SEQUENCES

    def runAllSequences(self):
        for sequence in self.__SEQUENCES:
            sequence.run(self.CONF)

    def getSequenceByDesc(self, desc):
        for sequence in self.getAllSequences():
            if sequence.name == desc:
                return sequence
        return None

    def __getSequenceIndexByDesc(self, desc):
        for sequence in self.getAllSequences():
            if sequence.name == desc:
                return self.__SEQUENCES.index(sequence)
        return None

    def insertSequenceBeforeSequence(self, sequenceName, desc, cond, cond_match, steps):
        """
        Insert a sequence before a named sequence.
        i.e. if the specified sequence name is "update x", the new
        sequence will be inserted BEFORE "update x"
        """
        index = self.__getSequenceIndexByDesc(sequenceName)
        if index == None:
            index = len(self.getAllSequences())
        self.__SEQUENCES.insert(index, Sequence(desc,
                                                steps_new_format(steps),
                                                condition=cond,
                                                cond_match=cond_match))

    # Groups and params
    def addGroup(self, group, params):
        self.__GROUPS.append(Group(group, params))

    def getGroupByName(self, groupName):
        for group in self.getAllGroups():
            if group.GROUP_NAME == groupName:
                return group
        return None

    def getAllGroups(self):
        return self.__GROUPS

    def __getGroupIndexByDesc(self, name):
        for group in self.getAllGroups():
            if group.GROUP_NAME == name:
                return self.__GROUPS.index(group)
        return None

    def insertGroupBeforeGroup(self, groupName, group, params):
        """
        Insert a group before a named group.
        i.e. if the specified group name is "update x", the new
        group will be inserted BEFORE "update x"
        """
        index = self.__getGroupIndexByDesc(groupName)
        if index == None:
            index = len(self.getAllGroups())
        self.__GROUPS.insert(index, Group(group, params))

    def getParamByName(self, paramName):
        for group in self.getAllGroups():
            if paramName in group.parameters:
                return group.parameters[paramName]
        return None

    def getParamKeyValue(self, paramName, keyName):
        param = self.getParamByName(paramName)
        if param:
            return getattr(param, keyName)
        else:
            return None
