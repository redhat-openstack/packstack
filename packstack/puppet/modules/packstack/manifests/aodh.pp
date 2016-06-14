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

    class { '::aodh::api':
      enabled               => true,
      keystone_password     => hiera('CONFIG_AODH_KS_PW'),
      keystone_identity_uri => hiera('CONFIG_KEYSTONE_ADMIN_URL'),
      service_name          => 'httpd',
    }

    class { '::aodh::wsgi::apache':
      workers => hiera('CONFIG_SERVICE_WORKERS'),
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
}
