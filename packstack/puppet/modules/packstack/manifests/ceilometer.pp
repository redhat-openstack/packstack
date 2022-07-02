class packstack::ceilometer ()
{
    create_resources(packstack::firewall, lookup('FIREWALL_CEILOMETER_RULES', undef, undef, {}))

    $config_ceilometer_coordination_backend = lookup('CONFIG_CEILOMETER_COORDINATION_BACKEND')

    $config_gnocchi_host = lookup('CONFIG_KEYSTONE_HOST_URL')

    if ($::operatingsystem == 'Fedora') or
      ($::osfamily == 'RedHat' and Integer.new($::operatingsystemmajrelease) > 7) {
      $pyvers = '3'
    } else {
      $pyvers = ''
    }

    if $config_ceilometer_coordination_backend == 'redis' {
      $redis_host = lookup('CONFIG_REDIS_HOST_URL')
      $redis_port = lookup('CONFIG_REDIS_PORT')
      $coordination_url = "redis://${redis_host}:${redis_port}"

      ensure_packages('python-redis', {
        name   => "python${pyvers}-redis",
        tag    => 'openstack',
      })
    } else {
      $coordination_url = ''
    }

    include ceilometer

    exec {'ceilometer-db-upgrade':
      command   => 'ceilometer-upgrade',
      path      => ['/usr/bin', '/usr/sbin'],
      try_sleep => 10,
      tries     => 20
    }

    Keystone::Resource::Service_identity<||> -> Exec['ceilometer-db-upgrade']
      ~> Service['ceilometer-agent-notification']

    class { 'ceilometer::agent::notification':
      manage_event_pipeline     => true,
      event_pipeline_publishers => ['gnocchi://'],
    }

    class { 'ceilometer::agent::service_credentials':
      auth_url    => lookup('CONFIG_KEYSTONE_PUBLIC_URL_VERSIONLESS'),
      password    => lookup('CONFIG_CEILOMETER_KS_PW'),
      region_name => lookup('CONFIG_KEYSTONE_REGION'),
    }

    class { 'ceilometer::coordination':
      backend_url => $coordination_url,
    }

    class { 'ceilometer::agent::polling':
      manage_polling   => true,
    }
}
