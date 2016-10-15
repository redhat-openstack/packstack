class packstack::aodh ()
{
    create_resources(packstack::firewall, hiera('FIREWALL_AODH_RULES', {}))

    $config_aodh_coordination_backend = hiera('CONFIG_CEILOMETER_COORDINATION_BACKEND')

    if $config_aodh_coordination_backend == 'redis' {
      $redis_host = hiera('CONFIG_REDIS_HOST_URL')
      $redis_port = hiera('CONFIG_REDIS_PORT')
      $coordination_url = "redis://${redis_host}:${redis_port}"
    } else {
      $coordination_url = ''
    }

    class { '::aodh::keystone::authtoken':
      password => hiera('CONFIG_AODH_KS_PW'),
      auth_url => hiera('CONFIG_KEYSTONE_ADMIN_URL'),
    }

    class { '::aodh::api':
      enabled      => true,
      service_name => 'httpd',
    }

    class { '::aodh::wsgi::apache':
      workers => hiera('CONFIG_SERVICE_WORKERS'),
      ssl     => false
    }

    class { '::aodh::auth':
      auth_password => hiera('CONFIG_AODH_KS_PW'),
      auth_url => hiera('CONFIG_KEYSTONE_PUBLIC_URL_VERSIONLESS'),
    }
    class { '::aodh::evaluator':
      coordination_url => $coordination_url,
    }
    class { '::aodh::notifier': }
    class { '::aodh::listener': }
    class { '::aodh::client': }
}
