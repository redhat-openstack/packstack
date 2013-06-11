
$warning = "Kernel package with netns support has been installed on host $::ipaddress. Please note that with this action you are loosing Red Hat support for this host. Because of the kernel update host mentioned above requires reboot."

class { 'packstack::netns':
    warning => $warning
}
