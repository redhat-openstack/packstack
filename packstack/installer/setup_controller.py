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

    __GROUPS = []
    __SEQUENCES = []
    __PLUGINS = []
    MESSAGES = []
    CONF = {}

    __single = None  # the one, true Singleton ... for god's sake why ??? :)

    def __new__(self, *args, **kwargs):
        """
        Singleton implementation.
        Will return __single if self is the same class as the class of __single
        which means that we will not invoke this singleton if someone tries to create a new
        instance from a class which inherit Controller.
        did not use isinstance because inheritence makes it behave erratically.
        """
        if self != type(self.__single):  # noqa: E721
            self.__single = object.__new__(self, *args, **kwargs)
        return self.__single

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
            sequence.run(config=self.CONF, messages=self.MESSAGES)

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
        if index is None:
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
        if index is None:
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
