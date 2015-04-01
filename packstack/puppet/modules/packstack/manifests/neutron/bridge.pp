
# Loads bridge modules and sets appropriate sysctl.conf variables

class packstack::neutron::bridge {
  file { 'bridge-module-loader':
    ensure  => file,
    path    => '/etc/sysconfig/modules/openstack-neutron.modules',
    mode    => '0700',
    content => template('packstack/openstack-neutron.modules.erb'),
  } -> exec { 'load-bridge':
    path      => ['/sbin', '/usr/sbin'],
    command   => 'modprobe -b bridge',
    logoutput => 'on_failure',
  } -> exec { 'load-bridge-netfilter':
    path      => ['/sbin', '/usr/sbin', '/bin', '/usr/bin'],
    command   => 'modprobe -b br_netfilter',
    logoutput => 'on_failure',
    unless    => 'test -d /proc/sys/net/bridge',
  } -> file_line { '/etc/sysctl.conf bridge-nf-call-ip6tables':
    path  => '/etc/sysctl.conf',
    line  => 'net.bridge.bridge-nf-call-ip6tables=1',
    match => 'net.bridge.bridge-nf-call-ip6tables\s*=',
  } -> file_line { '/etc/sysctl.conf bridge-nf-call-iptables':
    path  => '/etc/sysctl.conf',
    line  => 'net.bridge.bridge-nf-call-iptables=1',
    match => 'net.bridge.bridge-nf-call-iptables\s*=',
  } -> file_line { '/etc/sysctl.conf bridge-nf-call-arptables':
    path  => '/etc/sysctl.conf',
    line  => 'net.bridge.bridge-nf-call-arptables=1',
    match => 'net.bridge.bridge-nf-call-arptables\s*=',
  } -> exec { 'sysctl_refresh':
    path      => ['/usr/sbin', '/sbin', '/usr/bin', '/bin'],
    command   => 'sysctl -p /etc/sysctl.conf',
    logoutput => 'on_failure',
  }
}
