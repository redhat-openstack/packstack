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

import logging
import os
import re

from packstack.installer.exceptions import PuppetError


# TODO: Fill logger name when logging system will be refactored
logger = logging.getLogger()

re_color = re.compile('\x1b.*?\d\dm')
re_error = re.compile(
    'err:|Syntax error at|^Duplicate definition:|^Invalid tag|'
    '^No matching value for selector param|^Parameter name failed:|Error:|'
    '^Invalid parameter|^Duplicate declaration:|^Could not find resource|'
    '^Could not parse for|^/usr/bin/puppet:\d+: .+|.+\(LoadError\)|'
    '^Could not autoload|'
    '^\/usr\/bin\/env\: jruby\: No such file or directory|'
    'failed to execute puppet'
)
re_ignore = re.compile(
    # Puppet preloads a provider using the mysql command before it is installed
    'Command mysql is missing|'
    # Puppet preloads a database_grant provider which fails if /root/.my.cnf
    # is missing, this is ok because it will be retried later if needed
    'Could not prefetch database_grant provider.*?\\.my\\.cnf|'
    # Swift Puppet module tries to install swift-plugin-s3, there is no such
    # package on RHEL, fixed in the upstream puppet module
    'yum.*?install swift-plugin-s3|'
    # facter gives a weird NM error when it's disabled, due to
    # https://tickets.puppetlabs.com/browse/FACT-697
    'NetworkManager is not running'
)
re_notice = re.compile(r"notice: .*Notify\[packstack_info\]"
                       "\/message: defined \'message\' as "
                       "\'(?P<message>.*)\'")

surrogates = [
    # Value in /etc/sysctl.conf cannot be changed
    ('Sysctl::Value\[.*\]\/Sysctl\[(?P<arg1>.*)\].*Field \'val\' is required',
        'Cannot change value of %(arg1)s in /etc/sysctl.conf'),
    # Package is not found in yum repos
    ('Package\[.*\]\/ensure.*yum.*install (?P<arg1>.*)\'.*Nothing to do',
        'Package %(arg1)s has not been found in enabled Yum repos.'),
    ('Execution of \'.*yum.*install (?P<arg1>.*)\'.*Nothing to do',
        'Package %(arg1)s has not been found in enabled Yum repos.'),
    # Packstack does not cooperate with jruby
    ('jruby', 'Your Puppet installation uses jruby instead of ruby. Package '
              'jruby does not cooperate with Packstack well. You will have to '
              'fix this manually.'),
]


def validate_logfile(logpath):
    """
    Check given Puppet log file for errors and raise PuppetError if there is
    any error
    """
    manifestpath = os.path.splitext(logpath)[0]
    manifestfile = os.path.basename(manifestpath)
    with open(logpath) as logfile:
        for line in logfile:
            line = line.strip()

            if re_error.search(line) is None:
                continue

            error = re_color.sub('', line)  # remove colors
            if re_ignore.search(line):
                msg = ('Ignoring expected error during Puppet run %s: %s' %
                       (manifestfile, error))
                logger.debug(msg)
                continue

            for regex, surrogate in surrogates:
                match = re.search(regex, error)
                if match is None:
                    continue

                args = {}
                num = 1
                while True:
                    try:
                        args['arg%d' % num] = match.group(num)
                        num += 1
                    except IndexError:
                        break
                error = surrogate % args

            message = ('Error appeared during Puppet run: %s\n%s\n'
                       'You will find full trace in log %s' %
                       (manifestfile, error, logpath))
            raise PuppetError(message)


def scan_logfile(logpath):
    """
    Returns list of packstack_info/packstack_warn notices parsed from
    given puppet log file.
    """
    output = []
    with open(logpath) as logfile:
        for line in logfile:
            match = re_notice.search(line)
            if match:
                output.append(match.group('message'))
    return output
