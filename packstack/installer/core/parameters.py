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
Container set for groups and parameters
"""

from ..utils.datastructures import SortedDict


class Parameter(object):
    allowed_keys = ('CONF_NAME', 'CMD_OPTION', 'USAGE', 'PROMPT',
                    'PROCESSORS', 'VALIDATORS', 'LOOSE_VALIDATION',
                    'DEFAULT_VALUE', 'USE_DEFAULT', 'OPTION_LIST',
                    'MASK_INPUT', 'NEED_CONFIRM', 'CONDITION', 'DEPRECATES',
                    'MESSAGE', 'MESSAGE_VALUES')

    def __init__(self, attributes=None):
        attributes = attributes or {}
        defaults = {}.fromkeys(self.allowed_keys)
        defaults.update(attributes)

        for key, value in defaults.items():
            if key not in self.allowed_keys:
                raise KeyError('Given attribute %s is not allowed' % key)
            self.__dict__[key] = value


class Group(Parameter):
    allowed_keys = ('GROUP_NAME', 'DESCRIPTION', 'PRE_CONDITION',
                    'PRE_CONDITION_MATCH', 'POST_CONDITION',
                    'POST_CONDITION_MATCH')

    def __init__(self, attributes=None, parameters=None):
        super(Group, self).__init__(attributes)
        self.parameters = SortedDict()
        for param in parameters or []:
            self.parameters[param['CONF_NAME']] = Parameter(attributes=param)

    def search(self, attr, value):
        """
        Returns list of parameters which have given attribute of given
        value.
        """
        result = []
        for param in self.parameters.itervalues():
            if getattr(param, attr) == value:
                result.append(param)
        return result
