#!/bin/bash -ex
# Copyright 2015 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

SCENARIO=${SCENARIO:-scenario001}

# We could want to override the default repositories
MANAGE_REPOS=${MANAGE_REPOS:-true}
DELOREAN=${DELOREAN:-http://trunk.rdoproject.org/centos7/current-passed-ci/delorean.repo}
DELOREAN_DEPS=${DELOREAN_DEPS:-http://trunk.rdoproject.org/centos7/delorean-deps.repo}

if [ $(id -u) != 0 ]; then
    # preserve environment so we can have ZUUL_* params
    SUDO='sudo -E'
fi

# Setup repositories
if [ "${MANAGE_REPOS}" = true ]; then
    $SUDO curl ${DELOREAN} -o /etc/yum.repos.d/delorean.repo
    $SUDO curl ${DELOREAN_DEPS} -o /etc/yum.repos.d/delorean-deps.repo
fi

# Install dependencies
$SUDO yum -y install yum-plugin-priorities \
                     dstat \
                     python-setuptools \
                     openssl-devel \
                     python-devel \
                     libffi-devel \
                     libxml2-devel \
                     libxslt-devel \
                     ruby-devel \
                     openstack-selinux \
                     "@Development Tools"

# Setup dstat for resource usage tracing
if type "dstat" 2>/dev/null; then
  $SUDO dstat -tcmndrylpg \
              --top-cpu-adv \
              --top-io-adv \
              --nocolor | $SUDO tee --append /var/log/dstat.log > /dev/null &
fi

# Setup packstack
$SUDO python setup.py install
$SUDO python setup.py install_puppet_modules

# Generate configuration from selected scenario and run it
./tests/${SCENARIO}.sh
result=$?

# Generate subunit
pushd /var/lib/tempest
/var/lib/tempest/.venv/bin/testr last --subunit > /var/tmp/packstack/latest/testrepository.subunit
popd

exit $result
