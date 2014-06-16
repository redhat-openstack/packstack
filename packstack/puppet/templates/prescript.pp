include firewall

$el_releases = ["RedHat", "CentOS"]

# We don't have openstack-selinux package for Fedora and yet for RHEL-7
if $::operatingsystem != "Fedora" and ($::operatingsystem in $el_releases and $::operatingsystemrelease < 7) {
  package{ 'openstack-selinux':
    ensure => present,
  }
}

# For older RHEL-6 releases kernel/iptools does not support netns
if $::operatingsystem in $el_releases and $::operatingsystemrelease < 7 {
  $info = "The RDO kernel that includes network namespace (netns) support has been installed on host $::ipaddress."
  $warning = " This is a community supplied kernel and is not officially supported by Red Hat. Installing this kernel on RHEL systems may impact your ability to get support from Red Hat."

  class { 'packstack::netns':
    warning => "${info}${warning}"
  }
}

# Stop firewalld since everything uses iptables
# for now

service { "firewalld":
  ensure => "stopped",
  enable => false,
}

package { 'audit':
  ensure => present,
} ->
service { 'auditd':
  ensure => running,
  enable => true,
}

