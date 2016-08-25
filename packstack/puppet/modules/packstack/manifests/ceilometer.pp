class packstack::ceilometer ()
{
    create_resources(packstack::firewall, hiera('FIREWALL_CEILOMETER_RULES', {}))

    $config_mongodb_host = hiera('CONFIG_MONGODB_HOST_URL')

    $config_ceilometer_coordination_backend = hiera('CONFIG_CEILOMETER_COORDINATION_BACKEND')

    $config_ceilometer_metering_backend = hiera('CONFIG_CEILOMETER_METERING_BACKEND')

    $config_gnocchi_host = hiera('CONFIG_KEYSTONE_HOST_URL')

    if $config_ceilometer_coordination_backend == 'redis' {
      $redis_host = hiera('CONFIG_REDIS_HOST_URL')
      $redis_port = hiera('CONFIG_REDIS_PORT')
      $coordination_url = "redis://${redis_host}:${redis_port}"

      ensure_packages(['python-redis'], {'ensure' => 'present'})
    } else {
      $coordination_url = ''
    }

    if hiera('CONFIG_CEILOMETER_SERVICE_NAME') == 'ceilometer' {
          $ceilometer_service_name = 'openstack-ceilometer-api'
    } else {
          $ceilometer_service_name = 'httpd'
    }


    class { '::ceilometer::db':
      database_connection => "mongodb://${config_mongodb_host}:27017/ceilometer",
    }

    class { '::ceilometer::collector':
      meter_dispatcher => $config_ceilometer_metering_backend,
    }

    if $config_ceilometer_metering_backend == 'gnocchi' {

      include ::gnocchi::client
      class { '::ceilometer::dispatcher::gnocchi':
        filter_service_activity   => false,
        url                       => "http://${config_gnocchi_host}:8041",
        archive_policy            => 'high',
        resources_definition_file => 'gnocchi_resources.yaml',
      }
    }

    class { '::ceilometer::agent::notification': }

    class { '::ceilometer::agent::auth':
      auth_url      => hiera('CONFIG_KEYSTONE_PUBLIC_URL_VERSIONLESS'),
      auth_password => hiera('CONFIG_CEILOMETER_KS_PW'),
      auth_region   => hiera('CONFIG_KEYSTONE_REGION'),
    }

    class { '::ceilometer::agent::central':
      coordination_url => $coordination_url,
    }

    $bind_host = hiera('CONFIG_IP_VERSION') ? {
      'ipv6'  => '::0',
      default => '0.0.0.0',
      # TO-DO(mmagr): Add IPv6 support when hostnames are used
    }

    class { '::ceilometer::keystone::authtoken':
      auth_uri => hiera('CONFIG_KEYSTONE_PUBLIC_URL'),
      auth_url => hiera('CONFIG_KEYSTONE_ADMIN_URL'),
      password => hiera('CONFIG_CEILOMETER_KS_PW'),
    } ->
    class { '::ceilometer::api':
      host         => $bind_host,
      api_workers  => hiera('CONFIG_SERVICE_WORKERS'),
      service_name => $ceilometer_service_name,
    }

    if $ceilometer_service_name == 'httpd' {
       class { '::ceilometer::wsgi::apache':
         ssl => false,
       }
    }
}
