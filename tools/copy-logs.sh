#!/bin/bash
#
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
#
# See the License for the specific language governing permissions and
# limitations under the License.

export PATH=$PATH:/usr/local/sbin:/usr/sbin

# This script attempts to recover as much generic diagnostic logs as it can
LOGROOT=${WORKSPACE:-/tmp}
LOGDIR="${LOGROOT}/logs"
DIAG_LOGDIR="${LOGDIR}/diag"
CONF_LOGDIR="${LOGDIR}/etc"
GIT_URL="https://opendev.org"
PROJECTS_URL="${GIT_URL}/openstack/governance/raw/branch/master/reference/projects.yaml"

if [ $(id -u) != 0 ]; then
    SUDO='sudo'
fi

type -p dnf && export PKG_MGR=dnf || export PKG_MGR=yum

$SUDO mkdir -p "${DIAG_LOGDIR}"
$SUDO mkdir -p "${CONF_LOGDIR}"

function get_diag_commands {
    echo "Setting up list of diagnostic commands to run..."
    commands=(
        'df -h'
        'dmesg -T'
        'fdisk -l'
        'lsmod'
        'iptables -vnL'
        'iptables -vnL -t nat'
        'iptables -vnL -t mangle'
        'ifconfig -a'
        'ip addr show'
        'ip netns'
        'lsmod'
        'timeout 15 lsof' # High potential of getting stuck
        'lsof -Pni'
        'netstat -ntlp'
        'pstree -p'
        'sysctl -a'
        "$PKG_MGR repolist -v"
        'rpm -qa'
        'journalctl --no-pager'
        'ulimit -n'
        'dmidecode'
    )

    echo "Installing required RPM packages..."
    $SUDO $PKG_MGR -y install coreutils curl file lsof net-tools psmisc

    echo "Running diagnostic commands..."
    for ((i = 0; i < ${#commands[@]}; i++)); do
        # filenames have underscores instead of spaces or slashes
        filename="$(echo "${commands[$i]}" |sed -e "s%[ \/]%_%g").txt"
        # Run diagnostic commands but don't fail the whole thing if one command fails
        $SUDO bash -c "${commands[$i]} 2>&1 > ${DIAG_LOGDIR}/${filename}" || true
    done
}

function get_config_and_logs {
    echo "Setting up and discovering directories and files to recover..."
    # Paths we're interested in
    paths=(
        '/proc/cpuinfo'
        '/proc/meminfo'
        '/proc/mounts'
        '/etc/os-release'
        '/etc/sudoers'
        '/etc/sudoers.d'
        '/etc/hosts'
        '/etc/pip.conf'
        '/etc/libvirt'
        '/var/log/libvirt'
        '/etc/qemu'
        '/etc/qemu-kvm'
        '/etc/openvswitch'
        '/var/log/openvswitch'
        '/etc/openstack-dashboard'
        '/etc/aodh' # aodh is nested under telemetry in governance
        '/var/log/aodh'
        '/etc/ceilometer' # ceilometer is nested under telemetry in governance
        '/var/log/ceilometer'
        '/etc/gnocchi' # gnocchi is nested under telemetry in governance
        '/var/log/gnocchi'
        '/etc/rabbitmq/'
        '/var/log/rabbitmq'
        '/etc/redis'
        '/var/log/redis'
        '/etc/my.cnf.d'
        '/var/log/mariadb'
        '/etc/httpd/conf.d/'
        '/etc/yum.repos.d/'
        '/var/log/httpd'
        '/var/tmp/packstack/latest'
        '/var/tmp/packstack/latest/testrepository.subunit' # So we're copying it
        '/var/log/audit'                                   # to the root of
        '/var/log/secure'                                  # /logs
        '/var/log/messages'
        '/var/log/dstat.log'
        '/var/log/dnf.log'
        '/var/log/dnf.rpm.log'
        '/var/log/dnf.librepo.log'
        '/etc/puppet/puppet.conf'
        '/etc/puppet/hiera.yaml'
    )

    # Add discovered project directories from official governance
    # Optimistic parsing.. find a better way
    project_list=$(curl $PROJECTS_URL 2>&1 | egrep "^\S+:$" |cut -f1 -d :)
    for project in $project_list; do
        paths+=("/etc/${project}")
        paths+=("/var/log/${project}")
    done

    echo "Recovering files and directories..."
    # Send things to appropriate log directories if they exist
    for ((i = 0; i < ${#paths[@]}; i++)); do
        if [ -e ${paths[$i]} ]; then
            if [[ "${paths[$i]}" =~ /proc/ ]]; then
                $SUDO cp "${paths[$i]}" ${DIAG_LOGDIR}/
            elif [[ "${paths[$i]}" =~ /var/ ]]; then
                $SUDO cp -Lr "${paths[$i]}" ${LOGDIR}/
            elif [[ "${paths[$i]}" =~ /etc/ ]]; then
                $SUDO cp -Lr "${paths[$i]}" ${CONF_LOGDIR}/
            fi
        fi
    done
}

function ensure_log_properties {
    echo "Making sure directories and files have the right properties..."
    FIND="${SUDO} find ${LOGDIR} ! -path '*.git/*'"
    # Ensure files are readable by everyone
    $FIND -type d -execdir $SUDO chmod 755 '{}' \;
    $FIND -type f -execdir $SUDO chmod 644 '{}' \;

    # Ensure files are in .txt when possible (web mime type)
    for file in $($FIND -type f ! -name "*.txt"); do
        if [[ "$(file --mime-type ${file} |cut -f2 -d :)" =~ text ]]; then
            $SUDO mv ${file} ${file}.txt
        fi
    done
}

function recover_default_logs {
    get_diag_commands
    get_config_and_logs
    ensure_log_properties
}
