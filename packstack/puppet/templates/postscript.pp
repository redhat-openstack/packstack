exec { 'persist-firewall':
  command => '/sbin/iptables-save > /etc/sysconfig/iptables',
}

exec { 'update-selinux-policy':
    path => "/usr/bin/",
    command => "yum update -y selinux-policy-targeted"
}
