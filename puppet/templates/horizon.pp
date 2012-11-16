
class {'horizon':
   secret_key => '%(CONFIG_HORIZON_SECRET_KEY)s',
   keystone_host => '%(CONFIG_KEYSTONE_HOST)s',
}

class {'memcached':}

class {'apache':}
class {'apache::mod::wsgi':}
file { '/etc/httpd/conf.d/openstack-dashboard.conf':}

firewall { '001 horizon incomming':
    proto    => 'tcp',
    dport    => ['80'],
    action   => 'accept',
}

selboolean{'httpd_can_network_connect':
    value => on,
    persistent => true,
}
