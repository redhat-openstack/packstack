exec { 'persist-firewall':
  command => '/sbin/iptables-save > /etc/sysconfig/iptables',
}
