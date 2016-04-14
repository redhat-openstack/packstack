$config_aodh_coordination_backend = hiera('CONFIG_CEILOMETER_COORDINATION_BACKEND')

if $config_aodh_coordination_backend == 'redis' {
  $redis_ha = hiera('CONFIG_REDIS_HA')
  $redis_host = hiera('CONFIG_REDIS_MASTER_HOST_URL')
  $redis_port = hiera('CONFIG_REDIS_PORT')
  $sentinel_host = hiera('CONFIG_REDIS_SENTINEL_CONTACT_HOST')
  $sentinel_host_url = hiera('CONFIG_REDIS_SENTINEL_CONTACT_HOST_URL')
  $sentinel_fallbacks = hiera('CONFIG_REDIS_SENTINEL_FALLBACKS')
  if ($sentinel_host != '' and $redis_ha == 'y') {
    $master_name = hiera('CONFIG_REDIS_MASTER_NAME')
    $sentinel_port = hiera('CONFIG_REDIS_SENTINEL_PORT')
    $base_coordination_url = "redis://${sentinel_host_url}:${sentinel_port}?sentinel=${master_name}"
    if $sentinel_fallbacks != '' {
      $coordination_url = "${base_coordination_url}&${sentinel_fallbacks}"
    } else {
      $coordination_url = $base_coordination_url
    }
  } else {
    $coordination_url = "redis://${redis_host}:${redis_port}"
  }
} else {
  $coordination_url = ''
}

class { '::aodh::api':
  enabled               => true,
  keystone_password     => hiera('CONFIG_AODH_KS_PW'),
  keystone_identity_uri => hiera('CONFIG_KEYSTONE_ADMIN_URL'),
  service_name          => 'httpd',
}

class { '::apache':
   purge_configs => false,
}

class { '::aodh::wsgi::apache':
  workers => $service_workers,
  ssl     => false
}

class { '::aodh::auth':
  auth_password => hiera('CONFIG_AODH_KS_PW'),
}
class { '::aodh::evaluator':
  coordination_url => $coordination_url,
}
class { '::aodh::notifier': }
class { '::aodh::listener': }
class { '::aodh::client': }


