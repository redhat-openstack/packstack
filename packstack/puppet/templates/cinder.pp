
class {'cinder::base':
    rabbit_password => '',
    sql_connection => "mysql://cinder:cinder_default_password@%(CONFIG_MYSQL_HOST)s/cinder"
}

class {'cinder::api':
    keystone_password => 'cinder_default_password',
    keystone_tenant => "services",
    keystone_user => "cinder",
    keystone_auth_host => "%(CONFIG_KEYSTONE_HOST)s",
}

class {'cinder::scheduler':
}

class {'cinder::volume':
}

class {'cinder::volume::iscsi':
    iscsi_ip_address => '%(CONFIG_CINDER_HOST)s'
}

firewall { '001 cinder incomming':
    proto    => 'tcp',
    dport    => ['3260', '8776'],
    action   => 'accept',
}

