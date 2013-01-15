exec { 'persist-firewall':
  command     => $operatingsystem ? {
    'debian'          => '/sbin/iptables-save > /etc/iptables/rules.v4',
    /(fedora|RedHat|CentOS)/ 		  => '/sbin/iptables-save > /etc/sysconfig/iptables',
  },
}