include firewall

if $::operatingsystem != "Fedora" {
    package{ 'openstack-selinux':
        ensure => present,
    }
}

$info = "The RDO kernel that includes network namespace (netns) support has been installed on host $::ipaddress."
if $::operatingsystem == 'RedHat' {
    $warning = " This is a community supplied kernel and is not officially supported by Red Hat. Installing this kernel on RHEL systems may impact your ability to get support from Red Hat."
} else {
    $warning = ""
}

class { 'packstack::netns':
    warning => "${info}${warning}"
}
