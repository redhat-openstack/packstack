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
Base class for steps & sequences
"""

import logging
import sys
import traceback

from .. import utils
from ..exceptions import SequenceError


class Step(object):
    """
    Wrapper for function representing single setup step.
    """
    def __init__(self, name, function, title=None):
        self.name = name
        self.title = title or ('Step: %s' % name)

        # process step function
        if function and not callable(function):
            raise SequenceError("Function object have to be callable. "
                                "Object %s is not callable." % function)
        self.function = function

    def run(self, config=None, messages=None):
        config = config if config is not None else {}
        messages = messages if messages is not None else []
        # TO-DO: complete logger name when logging will be setup correctly
        logger = logging.getLogger()
        logger.debug('Running step %s.' % self.name)

        # execute and report state
        try:
            self.function(config, messages)
        except Exception:
            logger.debug(traceback.format_exc())
            state = utils.state_message(self.title, 'ERROR', 'red')
            sys.stdout.write('%s\n' % state)
            sys.stdout.flush()
            raise
        else:
            state = utils.state_message(self.title, 'DONE', 'green')
            sys.stdout.write('%s\n' % state)
            sys.stdout.flush()


class Sequence(object):
    """
    Wrapper for sequence of setup steps.
    """
    def __init__(self, name, steps, title=None, condition=None,
                 cond_match=None):
        self.name = name
        self.title = title
        self.condition = condition
        self.cond_match = cond_match

        # process sequence steps
        self.steps = utils.SortedDict()
        for step in steps:
            name, func = step['name'], step['function']
            self.steps[name] = Step(name, func, title=step.get('title'))

    def validate_condition(self, config):
        """
        Returns True if config option condition has value given
        in cond_match. Otherwise returns False.
        """
        if not self.condition:
            return True
        result = config.get(self.condition)
        return result == self.cond_match

    def run(self, config=None, messages=None, step=None):
        """
        Runs sequence of steps. Runs only specific step if step's name
        is given via 'step' parameter.
        """
        config = config if config is not None else {}
        messages = messages if messages is not None else []
        if not self.validate_condition(config):
            return
        if step:
            self.steps[step].run(config=config, messages=messages)
            return

        logger = logging.getLogger()
        logger.debug('Running sequence %s.' % self.name)
        if self.title:
            sys.stdout.write('%s\n' % self.title)
            sys.stdout.flush()
        for step in self.steps.itervalues():
            step.run(config=config, messages=messages)
