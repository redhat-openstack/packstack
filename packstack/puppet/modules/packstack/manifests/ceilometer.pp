class packstack::ceilometer ()
{
    create_resources(packstack::firewall, hiera('FIREWALL_CEILOMETER_RULES', {}))

    $config_ceilometer_coordination_backend = hiera('CONFIG_CEILOMETER_COORDINATION_BACKEND')

    $config_gnocchi_host = hiera('CONFIG_KEYSTONE_HOST_URL')

    if $config_ceilometer_coordination_backend == 'redis' {
      $redis_host = hiera('CONFIG_REDIS_HOST_URL')
      $redis_port = hiera('CONFIG_REDIS_PORT')
      $coordination_url = "redis://${redis_host}:${redis_port}"

      ensure_resource('package', 'python-redis', {
        name   => 'python-redis',
        tag    => 'openstack',
      })
    } else {
      $coordination_url = ''
    }

    include ::ceilometer

    exec {'ceilometer-db-upgrade':
      command   => 'ceilometer-upgrade',
      path      => ['/usr/bin', '/usr/sbin'],
      try_sleep => 10,
      tries     => 20
    }

    Keystone::Resource::Service_identity<||> -> Exec['ceilometer-db-upgrade'] ~>
      Service['ceilometer-agent-notification']

    class { '::ceilometer::agent::notification':
      manage_event_pipeline     => true,
      event_pipeline_publishers => ["gnocchi://", "panko://"],
    }

    class { '::ceilometer::agent::auth':
      auth_url      => hiera('CONFIG_KEYSTONE_PUBLIC_URL_VERSIONLESS'),
      auth_password => hiera('CONFIG_CEILOMETER_KS_PW'),
      auth_region   => hiera('CONFIG_KEYSTONE_REGION'),
    }

    class { '::ceilometer::agent::central':
      coordination_url => $coordination_url,
    }

    class { '::ceilometer::keystone::authtoken':
      auth_uri => hiera('CONFIG_KEYSTONE_PUBLIC_URL'),
      auth_url => hiera('CONFIG_KEYSTONE_ADMIN_URL'),
      password => hiera('CONFIG_CEILOMETER_KS_PW'),
    }
}
