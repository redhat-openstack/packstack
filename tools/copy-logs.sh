#!/bin/bash -xe
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

# This script attempts to recover as much generic diagnostic logs as it can
LOGROOT=${WORKSPACE:-/tmp}
LOGDIR="${LOGROOT}/logs"
DIAG_LOGDIR="${LOGDIR}/diag"
CONF_LOGDIR="${LOGDIR}/etc"
GIT_URL="http://git.openstack.org/cgit"
PROJECTS_URL="${GIT_URL}/openstack/governance/plain/reference/projects.yaml"

if [ $(id -u) != 0 ]; then
    SUDO='sudo -E'
fi
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
        'lsmod'
        'timeout 15 lsof' # High potential of getting stuck
        'lsof -Pni'
        'netstat -ntlp'
        'pstree -p'
        'sysctl -a'
        'yum repolist -v'
        'rpm -qa'
        'journalctl --no-pager'
    )

    echo "Installing required RPM packages..."
    yum -y install coreutils curl file iproute lsof net-tools psmisc

    echo "Running diagnostic commands..."
    for ((i = 0; i < ${#commands[@]}; i++)); do
        # filenames have underscores instead of spaces or slashes
        filename="$(echo "${commands[$i]}" |sed -e "s%[ \/]%_%g").txt"
        $SUDO ${commands[$i]} 2>&1 > ${DIAG_LOGDIR}/${filename}
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
        '/etc/mysql'
        '/var/log/mysql'
        '/var/log/mysql.err'
        '/var/log/mysql.log'
        '/etc/httpd'
        '/var/log/httpd'
        '/var/tmp/packstack'
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
                $SUDO cp -r "${paths[$i]}" ${LOGDIR}/
            elif [[ "${paths[$i]}" =~ /etc/ ]]; then
                $SUDO cp -r "${paths[$i]}" ${CONF_LOGDIR}/
            fi
        fi
    done
}

function ensure_log_properties {
    echo "Making sure directories and files have the right properties..."
    # Ensure files are in .txt when possible (web mime type)
    for file in $(find ${LOGDIR} -type f ! -name "*.txt"); do
        if [[ "$(file --mime-type ${file} |cut -f2 -d :)" =~ text ]]; then
            $SUDO mv ${file} ${file}.txt
        fi
    done

    # Ensure files are readable by everyone
    $SUDO find $LOGDIR -type d -execdir $SUDO chmod 755 '{}' \;
    $SUDO find $LOGDIR -type f -execdir $SUDO chmod 644 '{}' \;

    echo "Compressing all text files..."
    # Compress all files
    $SUDO find $LOGDIR -iname '*.txt' -execdir gzip -9 {} \+

    echo "Compressed log and configuration can be found in ${LOGDIR}."
}

function recover_default_logs {
    get_diag_commands
    get_config_and_logs
    ensure_log_properties
}
