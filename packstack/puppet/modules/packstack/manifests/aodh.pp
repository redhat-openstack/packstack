class packstack::aodh ()
{
    create_resources(packstack::firewall, lookup('FIREWALL_AODH_RULES', undef, undef, {}))

    $config_aodh_coordination_backend = lookup('CONFIG_CEILOMETER_COORDINATION_BACKEND')

    if $config_aodh_coordination_backend == 'redis' {
      $redis_host = lookup('CONFIG_REDIS_HOST_URL')
      $redis_port = lookup('CONFIG_REDIS_PORT')
      $coordination_url = "redis://${redis_host}:${redis_port}"
      Service<| title == 'redis' |> -> Anchor['aodh::service::begin']
    } else {
      $coordination_url = ''
    }

    class { 'aodh::keystone::authtoken':
      password             => lookup('CONFIG_AODH_KS_PW'),
      www_authenticate_uri => lookup('CONFIG_KEYSTONE_PUBLIC_URL_VERSIONLESS'),
      auth_url             => lookup('CONFIG_KEYSTONE_ADMIN_URL'),
    }

    class { 'aodh::api':
      enabled      => true,
      service_name => 'httpd',
      sync_db      => true,
    }

    class { 'aodh::wsgi::apache':
      workers => lookup('CONFIG_SERVICE_WORKERS'),
      ssl     => false
    }

    class { 'aodh::service_credentials':
      password    => lookup('CONFIG_AODH_KS_PW'),
      auth_url    => lookup('CONFIG_KEYSTONE_PUBLIC_URL_VERSIONLESS'),
      region_name => lookup('CONFIG_KEYSTONE_REGION'),
    }
    class { 'aodh::coordination':
      backend_url => $coordination_url,
    }
    class { 'aodh::evaluator': }
    class { 'aodh::notifier': }
    class { 'aodh::listener': }
    class { 'aodh::client': }
}
