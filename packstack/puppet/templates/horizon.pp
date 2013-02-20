
package {"horizon-packages":
    name => ["python-memcached", "python-netaddr"],
    notify => Class["horizon"],
}

file {"/etc/httpd/conf.d/rootredirect.conf":
    ensure => present,
    content => 'RedirectMatch ^/$ /dashboard/',
    notify => File["/etc/httpd/conf.d/openstack-dashboard.conf"],
}

class {'horizon':
   secret_key => '%(CONFIG_HORIZON_SECRET_KEY)s',
   keystone_host => '%(CONFIG_KEYSTONE_HOST)s',
}

class {'memcached':}

class {'apache':}
class {'apache::mod::wsgi':}
file { '/etc/httpd/conf.d/openstack-dashboard.conf':}
file { '/etc/httpd/conf.d/nagios.conf':}
file { '/etc/httpd/conf.d/php.conf':}

firewall { '001 horizon incoming':
    proto    => 'tcp',
    dport    => ['80'],
    action   => 'accept',
}

if ($::selinux != "false"){
    selboolean{'httpd_can_network_connect':
        value => on,
        persistent => true,
    }
}
