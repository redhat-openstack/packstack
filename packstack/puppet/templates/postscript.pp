exec { 'persist-firewall':
  command     => $operatingsystem ? {
    'debian'                  => '/sbin/iptables-save > /etc/iptables/rules.v4',
    /(Fedora|RedHat|CentOS|Scientific)/  => '/sbin/iptables-save > /etc/sysconfig/iptables',
  },
}
