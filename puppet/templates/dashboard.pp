
class {'horizon':
   secret_key => '%(DASHBOARD_SECRET_KEY)s',
   keystone_host => '%(CONFIG_KEYSTONE_HOST)s',
}

class {'memcached':}

firewall { '001 horizon incomming':
    proto    => 'tcp',
    dport    => ['80'],
    action   => 'accept',
}

selboolean{'httpd_can_network_connect':
    value => on,
    persistent => true,
}
