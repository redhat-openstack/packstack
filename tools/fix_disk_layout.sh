#!/bin/bash
# Copyright (C) 2016 OpenStack Foundation
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

# Don't attempt to fix disk layout more than once
[[ -e /etc/fixed_disk_layout ]] && return 0 || sudo touch /etc/fixed_disk_layout

# Ensure virtual machines from different providers all have at least 8GB of
# swap.
# Use an ephemeral disk if there is one or create and use a swapfile.
# Rackspace also doesn't have enough space on / for two devstack installs,
# so we partition the disk and mount it on /opt, syncing the previous
# contents of /opt over.
SWAPSIZE=8192
swapcurrent=$(( $(grep SwapTotal /proc/meminfo | awk '{ print $2; }') / 1024 ))

if [[ $swapcurrent -lt $SWAPSIZE ]]; then
    if [ -b /dev/xvde ]; then
        DEV='/dev/xvde'
    else
        EPHEMERAL_DEV=$(blkid -L ephemeral0 || true)
        if [ -n "$EPHEMERAL_DEV" -a -b "$EPHEMERAL_DEV" ]; then
            DEV=$EPHEMERAL_DEV
        fi
    fi
    if [ -n "$DEV" ]; then
        # If an ephemeral device is available, use it
        swap=${DEV}1
        lvmvol=${DEV}2
        optdev=${DEV}3
        if mount | grep ${DEV} > /dev/null; then
            echo "*** ${DEV} appears to already be mounted"
            echo "*** ${DEV} unmounting and reformating"
            sudo umount ${DEV}
        fi
        sudo parted ${DEV} --script -- mklabel msdos
        sudo parted ${DEV} --script -- mkpart primary linux-swap 1 ${SWAPSIZE}
        sudo parted ${DEV} --script -- mkpart primary ext2 8192 -1
        sudo mkswap ${DEV}1
        sudo mkfs.ext4 ${DEV}2
        sudo swapon ${DEV}1
        sudo mount ${DEV}2 /mnt
        sudo find /opt/ -mindepth 1 -maxdepth 1 -exec mv {} /mnt/ \;
        sudo umount /mnt
        sudo mount ${DEV}2 /opt

        # Sanity check
        grep -q ${DEV}1 /proc/swaps || exit 1
        grep -q ${DEV}2 /proc/mounts || exit 1
    else
        # If no ephemeral devices are available, use root filesystem
        # Don't use sparse device to avoid wedging when disk space and
        # memory are both unavailable.
        swapfile='/root/swapfile'
        swapdiff=$(( $SWAPSIZE - $swapcurrent ))

        sudo dd if=/dev/zero of=${swapfile} bs=1M count=${swapdiff}
        sudo chmod 600 ${swapfile}
        sudo mkswap ${swapfile}
        sudo swapon ${swapfile}

        # Sanity check
        grep -q ${swapfile} /proc/swaps || exit 1
    fi
fi

# dump vm settings for reference (Ubuntu 12 era procps can get
# confused with certain proc trigger nodes that are write-only and
# return a EPERM; ignore this)
sudo sysctl vm || true

# ensure a standard level of swappiness.  Some platforms
# (rax+centos7) come with swappiness of 0 (presumably because the
# vm doesn't come with swap setup ... but we just did that above),
# which depending on the kernel version can lead to the OOM killer
# kicking in on some processes despite swap being available;
# particularly things like mysql which have very high ratio of
# anonymous-memory to file-backed mappings.

# make sure reload of sysctl doesn't reset this
sudo sed -i '/vm.swappiness/d' /etc/sysctl.conf
# This sets swappiness low; we really don't want to be relying on
# cloud I/O based swap during our runs
sudo sysctl -w vm.swappiness=10
