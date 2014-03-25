class { 'ceilometer::db':
    database_connection => 'mongodb://%(CONFIG_MONGODB_HOST)s:27017/ceilometer',
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
