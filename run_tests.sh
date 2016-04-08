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

export PATH=$PATH:/usr/local/sbin:/usr/sbin

SCENARIO=${SCENARIO:-scenario001}

# We could want to override the default repositories or install behavior
INSTALL_FROM_SOURCE=${INSTALL_FROM_SOURCE:-true}
MANAGE_REPOS=${MANAGE_REPOS:-true}
DELOREAN=${DELOREAN:-http://trunk.rdoproject.org/centos7-mitaka/current-passed-ci/delorean.repo}
DELOREAN_DEPS=${DELOREAN_DEPS:-http://trunk.rdoproject.org/centos7-mitaka/delorean-deps.repo}

# If logs should be retrieved automatically
COPY_LOGS=${COPY_LOGS:-true}

if [ $(id -u) != 0 ]; then
    SUDO='sudo'

    # Packstack will connect as root to localhost, set-up the keypair and sshd
    ssh-keygen -t rsa -C "packstack-integration-test" -N "" -f ~/.ssh/id_rsa

    $SUDO mkdir -p /root/.ssh
    cat ~/.ssh/id_rsa.pub | $SUDO tee -a /root/.ssh/authorized_keys
    $SUDO chmod 0600 /root/.ssh/authorized_keys
    $SUDO sed -i 's/^PermitRootLogin no/PermitRootLogin without-password/g' /etc/ssh/sshd_config
    $SUDO service sshd restart
fi

# TODO: REMOVE ME
# https://github.com/openstack/diskimage-builder/blob/b5bcb3b60ec33c4538baa1aeacd026998b155ca6/elements/yum-minimal/pre-install.d/03-yum-cleanup#L26
$SUDO yum -y reinstall glibc-common

# Make swap configuration consistent
# TODO: REMOVE ME
# https://review.openstack.org/#/c/300122/
source ./tools/fix_disk_layout.sh

# Bump ulimit to avoid too many open file errors
echo "${USER} soft nofile 65536" | $SUDO tee -a /etc/security/limits.conf
echo "${USER} hard nofile 65536" | $SUDO tee -a /etc/security/limits.conf
echo "root soft nofile 65536" | $SUDO tee -a /etc/security/limits.conf
echo "root hard nofile 65536" | $SUDO tee -a /etc/security/limits.conf

# Setup repositories
if [ "${MANAGE_REPOS}" = true ]; then
    $SUDO curl ${DELOREAN} -o /etc/yum.repos.d/delorean.repo
    $SUDO curl ${DELOREAN_DEPS} -o /etc/yum.repos.d/delorean-deps.repo
fi

# Install dependencies
$SUDO yum -y install puppet \
                     yum-plugin-priorities \
                     iproute \
                     dstat \
                     python-setuptools \
                     openssl-devel \
                     python-devel \
                     libffi-devel \
                     libxml2-devel \
                     libxslt-devel \
                     libyaml-devel \
                     ruby-devel \
                     openstack-selinux \
                     policycoreutils \
                     "@Development Tools"

# TO-DO: Packstack should handle Hiera and Puppet configuration, so that it works
# no matter the environment
$SUDO su -c 'cat > /etc/puppet/puppet.conf <<EOF
[main]
    logdir = /var/log/puppet
    rundir = /var/run/puppet
    ssldir = $vardir/ssl
    hiera_config = /etc/puppet/hiera.yaml

[agent]
    classfile = $vardir/classes.txt
    localconfig = $vardir/localconfig
EOF'
$SUDO su -c 'cat > /etc/puppet/hiera.yaml <<EOF
---
:backends:
  - yaml
:yaml:
  :datadir: /placeholder
:hierarchy:
  - common
  - defaults
  - "%{clientcert}"
  - "%{environment}"
  - global
EOF'

# To make sure wrong config files are not used
if [ -d /home/jenkins/.puppet ]; then
  $SUDO rm -f /home/jenkins/.puppet
fi
$SUDO puppet config set hiera_config /etc/puppet/hiera.yaml

# Setup dstat for resource usage tracing
if type "dstat" 2>/dev/null; then
  $SUDO dstat -tcmndrylpg \
              --top-cpu-adv \
              --top-io-adv \
              --nocolor | $SUDO tee -a /var/log/dstat.log > /dev/null &
fi

# Setup packstack
if [ "${INSTALL_FROM_SOURCE}" = true ]; then
  $SUDO pip install .
  $SUDO python setup.py install_puppet_modules
else
  $SUDO yum -y install openstack-packstack
fi

# Generate configuration from selected scenario and run it
source ./tests/${SCENARIO}.sh
result=$?

# Print output and generate subunit if results exist
if [ -d /var/lib/tempest ]; then
    pushd /var/lib/tempest
    $SUDO .tox/all/bin/testr last || true
    $SUDO bash -c ".tox/all/bin/testr last --subunit > /var/tmp/packstack/latest/testrepository.subunit" || true
    popd
fi

if [ "${COPY_LOGS}" = true ]; then
    source ./tools/copy-logs.sh
    recover_default_logs
fi

if [ "${FAILURE}" = true ]; then
    exit 1
fi

exit $result
