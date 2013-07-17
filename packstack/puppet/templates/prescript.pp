
$warning = "Kernel package with netns support has been installed on host $::ipaddress. Please note that with this action you are losing Red Hat support for this host. Because of the kernel update the host mentioned above requires reboot."

class { 'packstack::netns':
    warning => $warning
}
