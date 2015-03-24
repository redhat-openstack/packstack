include firewall

$el_releases = ['RedHat', 'CentOS', 'Scientific']

# We don't have openstack-selinux package for Fedora
if $::operatingsystem != "Fedora" {
  package{ 'openstack-selinux':
    ensure => present,
  }
}

# For older RHEL-6 releases kernel/iptools does not support netns
if $::operatingsystem in $el_releases and $::operatingsystemmajrelease < 7 {
  $info = "The RDO kernel that includes network namespace (netns) support has been installed on host $::ipaddress."
  $warning = " This is a community supplied kernel and is not officially supported by Red Hat. Installing this kernel on RHEL systems may impact your ability to get support from Red Hat."

  class { 'packstack::netns':
    warning => "${info}${warning}"
  }
}

# Stop firewalld since everything uses iptables. Firewalld provider will
# have to be implemented in puppetlabs-firewall in future.
service { "firewalld":
  ensure => "stopped",
  enable => false,
  before => Service['iptables'],
}

package { 'audit':
  ensure => present,
} ->
service { 'auditd':
  ensure => running,
  enable => true,
}

