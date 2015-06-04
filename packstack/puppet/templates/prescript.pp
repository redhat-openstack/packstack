include ::firewall

# We don't have openstack-selinux package for Fedora
if $::operatingsystem != 'Fedora' {
  package{ 'openstack-selinux':
    ensure => present,
  }
}

package { 'sos':
  ensure => present,
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
