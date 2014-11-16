$config_mongodb_host = hiera('CONFIG_MONGODB_HOST')

$config_ceilometer_coordination_backend = hiera('CONFIG_CEILOMETER_COORDINATION_BACKEND')

if $config_ceilometer_coordination_backend == 'redis' {
  $redis_host = hiera('CONFIG_REDIS_HOST')
  $redis_port = hiera('CONFIG_REDIS_PORT')
  $coordination_url = "redis://${redis_host}:${redis_port}"
} else {
  $coordination_url = ''
}

class { 'ceilometer::db':
  database_connection => "mongodb://${config_mongodb_host}:27017/ceilometer",
}

class { 'ceilometer::collector': }

class { 'ceilometer::agent::notification': }

$config_controller_host = hiera('CONFIG_CONTROLLER_HOST')

class { 'ceilometer::agent::auth':
  auth_url      => "http://${config_controller_host}:35357/v2.0",
  auth_password => hiera('CONFIG_CEILOMETER_KS_PW'),
}

class { 'ceilometer::agent::central':
  coordination_url => $coordination_url,
}

class { 'ceilometer::alarm::notifier':}

class { 'ceilometer::alarm::evaluator':
  coordination_url => $coordination_url,
}

class { 'ceilometer::api':
  keystone_host     => hiera('CONFIG_CONTROLLER_HOST'),
  keystone_password => hiera('CONFIG_CEILOMETER_KS_PW'),
}
