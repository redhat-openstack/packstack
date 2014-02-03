class { 'mongodb::server':
    port         => '27017',
    smallfiles   => true,
    before       => Class['ceilometer::db'],
    require      => Firewall['001 mongodb incoming localhost'],
}

firewall { '001 mongodb incoming localhost':
    proto       => 'tcp',
    dport       => ['27017'],
    iniface     => 'lo',
    #source      => 'localhost',
    #destination => 'localhost',
    action      => 'accept',
}

class { 'ceilometer':
    metering_secret => '%(CONFIG_CEILOMETER_SECRET)s',
    qpid_hostname   => '%(CONFIG_QPID_HOST)s',
    qpid_username   => '%(CONFIG_QPID_AUTH_USER)s',
    qpid_password   => '%(CONFIG_QPID_AUTH_PASSWORD)s',
    rpc_backend     => 'ceilometer.openstack.common.rpc.impl_qpid',
    verbose         => true,
    debug           => %(CONFIG_DEBUG_MODE)s,
    qpid_port       => '%(CONFIG_QPID_CLIENTS_PORT)s',
    qpid_protocol   => '%(CONFIG_QPID_PROTOCOL)s'
}

class { 'ceilometer::db':
    database_connection => 'mongodb://localhost:27017/ceilometer',
    require             => Class['mongodb::server'],
}

class { 'ceilometer::collector':
    require => Class['mongodb::server'],
}

class { 'ceilometer::agent::auth':
    auth_url      => 'http://%(CONFIG_KEYSTONE_HOST)s:35357/v2.0',
    auth_password => '%(CONFIG_CEILOMETER_KS_PW)s',
}

class { 'ceilometer::agent::central':
}

class { 'ceilometer::alarm::notifier':
}

class { 'ceilometer::alarm::evaluator':
}

class { 'ceilometer::api':
    keystone_host     => '%(CONFIG_KEYSTONE_HOST)s',
    keystone_password => '%(CONFIG_CEILOMETER_KS_PW)s',
    require           => Class['mongodb::server'],
}
