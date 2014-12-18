include firewall

if $::ipaddress == hiera('CONFIG_CONTROLLER_HOST') {
  include ::apache
}

$el_releases = ['RedHat', 'CentOS', 'Scientific']

# We don't have openstack-selinux package for Fedora
if $::operatingsystem != 'Fedora' {
  package{ 'openstack-selinux':
    ensure => present,
  }
}

# For older RHEL-6 releases kernel/iptools does not support netns
if $::operatingsystem in $el_releases and $::operatingsystemmajrelease < 7 {
  $info = "The RDO kernel that includes network namespace (netns) support has been installed on host ${::ipaddress}."
  $warning = " This is a community supplied kernel and is not officially supported by Red Hat. Installing this kernel on RHEL systems may impact your ability to get support from Red Hat."

  class { 'packstack::netns':
    warning => "${info}${warning}"
  }
}

package { 'audit':
  ensure => present,
} ->
service { 'auditd':
  ensure => running,
  enable => true,
}

# The following kernel parameters help alleviate some RabbitMQ
# connection issues

sysctl::value { 'net.ipv4.tcp_keepalive_intvl':
  value => '1',
}

sysctl::value { 'net.ipv4.tcp_keepalive_probes':
  value => '5',
}

sysctl::value { 'net.ipv4.tcp_keepalive_time':
  value => '5',
}
