class packstack::cinder ()
{
    create_resources(packstack::firewall, lookup('FIREWALL_CINDER_RULES', undef, undef, {}))
    create_resources(packstack::firewall, lookup('FIREWALL_CINDER_API_RULES', undef, undef, {}))

    $cinder_backends = lookup('CONFIG_CINDER_BACKEND', { merge => 'unique' })

    case $cinder_backends[0] {
      'lvm':       { $default_volume_type = 'iscsi' }
      'nfs':       { $default_volume_type = 'nfs' }
      'vmdk':      { $default_volume_type = 'vmdk' }
      'netapp':    { $default_volume_type = 'netapp' }
      'solidfire': { $default_volume_type = 'solidfire' }
      default:     { $default_volume_type = 'iscsi' }
    }

    $bind_host = lookup('CONFIG_IP_VERSION') ? {
      'ipv6'  => '::0',
      default => '0.0.0.0',
      # TO-DO(mmagr): Add IPv6 support when hostnames are used
    }

    class { 'cinder::keystone::authtoken':
      www_authenticate_uri => lookup('CONFIG_KEYSTONE_PUBLIC_URL_VERSIONLESS'),
      auth_url             => lookup('CONFIG_KEYSTONE_ADMIN_URL'),
      password             => lookup('CONFIG_CINDER_KS_PW'),
    }

    class { 'cinder::api':
      bind_host           => $bind_host,
      service_workers     => lookup('CONFIG_SERVICE_WORKERS'),
      default_volume_type => $default_volume_type,
    }

    class { 'cinder::scheduler': }

    class { 'cinder::volume': }

    class { 'cinder::client': }

    class { 'cinder::glance': }

    class { 'cinder::nova':
      auth_type => 'password',
      password  => lookup('CONFIG_NOVA_KS_PW'),
      auth_url  => lookup('CONFIG_KEYSTONE_ADMIN_URL'),
    }

    class { 'cinder::keystone::service_user':
      send_service_user_token => true,
      password                => lookup('CONFIG_CINDER_KS_PW'),
      auth_url                => lookup('CONFIG_KEYSTONE_ADMIN_URL'),
    }

    class { 'cinder::backends':
      enabled_backends => lookup('CONFIG_CINDER_BACKEND', { merge => 'unique' }),
    }

    $db_purge = lookup('CONFIG_CINDER_DB_PURGE_ENABLE')
    if $db_purge {
      class { 'cinder::cron::db_purge':
        hour        => '*/24',
        destination => '/dev/null',
        age         => 1
      }
    }
}
