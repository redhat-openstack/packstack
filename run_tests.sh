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

BRANCH=master

# Find OS version and release
source /etc/os-release
OS_NAME_VERS=${ID}${VERSION_ID}

# We could want to override the default repositories or install behavior
INSTALL_FROM_SOURCE=${INSTALL_FROM_SOURCE:-true}
MANAGE_REPOS=${MANAGE_REPOS:-true}
DELOREAN=${DELOREAN:-https://trunk.rdoproject.org/${OS_NAME_VERS}-master/current-passed-ci/delorean.repo}
DELOREAN_DEPS=${DELOREAN_DEPS:-https://trunk.rdoproject.org/${OS_NAME_VERS}-master/delorean-deps.repo}
GIT_BASE_URL=${GIT_BASE_URL:-https://git.openstack.org}
ADDITIONAL_ARGS=${ADDITIONAL_ARGS:-}
SELINUX_ENFORCING=${SELINUX_ENFORCING:-true}
# If logs should be retrieved automatically
COPY_LOGS=${COPY_LOGS:-true}

# Let's add an option for a secondary node, to act as a compute
CONTROLLER_NODE=${CONTROLLER_NODE:-}
COMPUTE_NODE=${COMPUTE_NODE:-}

# Use dnf as package manager if it exist
type -p dnf && export PKG_MGR=dnf || export PKG_MGR=yum

# Install external Puppet modules with r10k
# Uses the following variables:
#
# - ``GEM_BIN_DIR`` must be set to Gem bin directory
# - ``PUPPETFILE_DIR`` must be set to Puppet modules directory
install_external() {
  $SUDO ${GEM_BIN_DIR}r10k puppetfile install -v --moduledir ${PUPPETFILE_DIR} --puppetfile Puppetfile1
}

# Install Puppet OpenStack modules with zuul-cloner
# Uses the following variables:
#
# - ``PUPPETFILE_DIR`` must be set to Puppet modules directory
# - ``ZUUL_REF`` must be set to Zuul ref. Fallback to 'None'.
# - ``ZUUL_BRANCH`` must be set to Zuul branch. Fallback to 'master'.
install_openstack() {
  cat > clonemap.yaml <<EOF
clonemap:
  - name: '(.*?)/puppet-(.*)'
    dest: '$PUPPETFILE_DIR/\2'
EOF

  # Periodic jobs run without ref on master
  ZUUL_REF=${ZUUL_REF:-None}
  ZUUL_BRANCH=${ZUUL_BRANCH:-master}
  GIT_BASE_URL=${GIT_BASE_URL:-https://git.openstack.org}

  local project_names=$(awk '{ if ($1 == ":git") print $3 }' \
    Puppetfile0 | tr -d "'," | cut -d '/' -f 4- | xargs
  )
  $SUDO /usr/zuul-env/bin/zuul-cloner -m clonemap.yaml \
    --cache-dir /opt/git \
    --zuul-ref $ZUUL_REF \
    --zuul-branch $ZUUL_BRANCH \
    https://git.openstack.org $project_names
}

# Install all Puppet modules with r10k
# Uses the following variables:
#
# - ``GEM_BIN_DIR`` must be set to Gem bin directory
install_all() {
  $SUDO ${GEM_BIN_DIR}r10k puppetfile install -v --puppetfile Puppetfile
}

# Install Puppet OpenStack modules and dependencies by using
# zuul-cloner or r10k.
# Uses the following variables:
#
# - ``PUPPETFILE_DIR`` must be set to Puppet modules directory
# - ``ZUUL_REF`` must be set to Zuul ref
# - ``ZUUL_BRANCH`` must be set to Zuul branch
install_modules() {
  # If zuul-cloner is there, have it install modules using zuul refs
  if [ -e /usr/zuul-env/bin/zuul-cloner ] ; then
    csplit Puppetfile /'Non-OpenStack modules'/ \
      --prefix Puppetfile \
      --suffix '%d'
    install_external
    install_openstack
  else
    install_all
  fi
  # Copy the Packstack Puppet module
  $SUDO cp -r packstack/puppet/modules/packstack ${PUPPETFILE_DIR}
}

if [ $(id -u) != 0 ]; then
    SUDO='sudo -E'

    # Packstack will connect as root to localhost, set-up the keypair and sshd
    if [ ! -f ~/.ssh/id_rsa ]; then
      ssh-keygen -t rsa -C "packstack-integration-test" -N "" -f ~/.ssh/id_rsa
    fi

    $SUDO mkdir -p /root/.ssh
    cat ~/.ssh/id_rsa.pub | $SUDO tee -a /root/.ssh/authorized_keys
    $SUDO chmod 0600 /root/.ssh/authorized_keys
    $SUDO sed -i 's/^PermitRootLogin no/PermitRootLogin without-password/g' /etc/ssh/sshd_config
    $SUDO service sshd restart
fi

# Make swap configuration consistent
# TODO: REMOVE ME
# https://review.openstack.org/#/c/300122/
source ./tools/fix_disk_layout.sh

# Bump ulimit to avoid too many open file errors
echo "${USER} soft nofile 65536" | $SUDO tee -a /etc/security/limits.conf
echo "${USER} hard nofile 65536" | $SUDO tee -a /etc/security/limits.conf
echo "root soft nofile 65536" | $SUDO tee -a /etc/security/limits.conf
echo "root hard nofile 65536" | $SUDO tee -a /etc/security/limits.conf

# Set SELinux to enforcing/permissive as needed
if [ "${SELINUX_ENFORCING}" = true ]; then
    $SUDO setenforce 1
else
    $SUDO setenforce 0
fi

# Setup repositories
if [ "${MANAGE_REPOS}" = true ]; then
    $SUDO curl -L ${DELOREAN} -o /etc/yum.repos.d/delorean.repo
    $SUDO curl -L ${DELOREAN_DEPS} -o /etc/yum.repos.d/delorean-deps.repo
    $SUDO $PKG_MGR update -y
fi

# Install dependencies
$SUDO $PKG_MGR -y install puppet \
                     iproute \
                     iptables \
                     iptables-services \
                     dstat \
                     openssl-devel \
                     libffi-devel \
                     libxml2-devel \
                     libxslt-devel \
                     libyaml-devel \
                     ruby-devel \
                     openstack-selinux \
                     policycoreutils \
                     rubygems \
                     curl \
                     gettext \
                     diffstat \
                     doxygen \
                     patch \
                     patchutils \
                     subversion \
                     systemtap

# Some dependencies are not installed on RHEL/CentOS 8, or are renamed
OS_NAME=$(facter operatingsystem)
OS_VERSION=$(facter operatingsystemmajrelease)

$SUDO $PKG_MGR -y install python3-setuptools \
                          python3-devel \
                          python3-wheel \
                          python3-pyyaml

# Don't assume pip is installed
which pip3 && PIP=pip3
if [ -z $PIP ]; then
    $SUDO $PKG_MGR -y install python3-pip python3-wheel
    PIP=pip3
fi

# Try to use pre-cached cirros images, if available, otherwise download them
rm -rf /tmp/cirros
mkdir /tmp/cirros

export CIRROS_ARCH="$(uname -p)"
export CIRROS_VERSION=${CIRROS_VERSION:-"0.6.3"}

if [ -f ~/cache/files/cirros-$CIRROS_VERSION-$CIRROS_ARCH-uec.tar.gz ]; then
    tar -xzvf ~/cache/files/cirros-$CIRROS_VERSION-$CIRROS_ARCH-uec.tar.gz -C /tmp/cirros/
else
    echo "No pre-cached uec archive found, downloading..."
    curl -Lo /tmp/cirros/cirros-$CIRROS_VERSION-$CIRROS_ARCH-uec.tar.gz --retry 10 https://download.cirros-cloud.net/$CIRROS_VERSION/cirros-$CIRROS_VERSION-$CIRROS_ARCH-uec.tar.gz
    tar -xzvf /tmp/cirros/cirros-$CIRROS_VERSION-$CIRROS_ARCH-uec.tar.gz -C /tmp/cirros/
fi
if [ -f ~/cache/files/cirros-$CIRROS_VERSION-$CIRROS_ARCH-disk.img ]; then
    cp -p ~/cache/files/cirros-$CIRROS_VERSION-$CIRROS_ARCH-disk.img /tmp/cirros/
else
    echo "No pre-cached disk image found, downloading..."
    curl -Lo /tmp/cirros/cirros-$CIRROS_VERSION-$CIRROS_ARCH-disk.img --retry 10 https://download.cirros-cloud.net/$CIRROS_VERSION/cirros-$CIRROS_VERSION-$CIRROS_ARCH-disk.img
fi
echo "Using pre-cached images:"
find /tmp/cirros -type f -printf "%m %n %u %g %s  %t" -exec md5sum \{\} \;

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
    DSTAT_OPTS=""
    set -e
    if dstat --help 2>&1 | grep -q "top-io-adv"; then
        DSTAT_OPTS="${DSTAT_OPTS} --top-io-adv"
    fi

    if dstat --help 2>&1 | grep -q "top-cpu-adv"; then
        DSTAT_OPTS="${DSTAT_OPTS} --top-cpu-adv"
    fi
    set +e
    $SUDO dstat -tcmndrylpg $DSTAT_OPTS --nocolor | $SUDO tee --append /var/log/dstat.log > /dev/null &
fi

# Setup packstack
if [ "${INSTALL_FROM_SOURCE}" = true ]; then
  $SUDO $PIP install -U pip
  $SUDO $PIP install --ignore-installed -c https://opendev.org/openstack/requirements/raw/branch/$BRANCH/upper-constraints.txt --prefix=/usr .
  # In Fedora when running with sudo gems are installed at /usr/local/bin/ even when GEM_HOME/GEM_BIN_DIR are set
  if [ "${PKG_MGR}" = "dnf" ]; then
      export GEM_BIN_DIR=/usr/local/bin/
  else
      export GEM_BIN_DIR=/tmp/packstackgems/bin/
  fi
  export PUPPETFILE_DIR=/usr/share/openstack-puppet/modules
  export GEM_HOME=/tmp/packstackgems
  $SUDO gem install r10k
  # make sure there is no puppet module pre-installed
  $SUDO rm -rf "${PUPPETFILE_DIR:?}/"*
  install_modules
else
  $SUDO $PKG_MGR -y install openstack-packstack
fi

# Make sure there are no other puppet modules in the system (happens in gate)
$SUDO rm -rf /etc/puppet/modules/*

# Make sure the fqdn is associated to the IP in /etc/hosts
# Needed for Horizon SSL tests in Tempest
echo -e "\n127.0.0.1 $(facter fqdn)" | $SUDO tee -a /etc/hosts

# Generate configuration from selected scenario and run it
source ./tests/${SCENARIO}.sh
result=$?

# Print output and generate subunit if results exist
if [ -d /var/lib/tempest ]; then
    # FIXME(jpena): Work around Fedora image issues with umask
    $SUDO chown -R $USER /var/lib/tempest
    pushd /var/lib/tempest
    if [ -d .testrepository ]; then
        $SUDO /usr/bin/testr last || true
        $SUDO bash -c "/usr/bin/testr last --subunit > /var/tmp/packstack/latest/testrepository.subunit" || true
    elif [ -d .stestr ]; then
        $SUDO /usr/bin/stestr last || true
        $SUDO bash -c "/usr/bin/stestr last --subunit > /var/tmp/packstack/latest/testrepository.subunit" || true
    fi
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
