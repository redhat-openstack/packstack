
class { 'mongodb':
    enable_10gen => false,
    port         => '27017',
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
    rpc_backend     => 'ceilometer.openstack.common.rpc.impl_qpid',
    verbose         => true,
    debug           => true,
}

class { 'ceilometer::db':
    database_connection => 'mongodb://localhost:27017/ceilometer',
    require             => Class['mongodb'],
}

class { 'ceilometer::collector':
    require => Class['mongodb'],
}

class { 'ceilometer::agent::central':
    auth_url      => 'http://%(CONFIG_KEYSTONE_HOST)s:35357/v2.0',
    auth_password => '%(CONFIG_CEILOMETER_KS_PW)s',
}

class { 'ceilometer::api':
    keystone_host     => '%(CONFIG_KEYSTONE_HOST)s',
    keystone_password => '%(CONFIG_CEILOMETER_KS_PW)s',
    require           => Class['mongodb'],
}
