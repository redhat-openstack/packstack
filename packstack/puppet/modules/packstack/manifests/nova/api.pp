class packstack::nova::api ()
{
    create_resources(packstack::firewall, lookup('FIREWALL_NOVA_API_RULES', undef, undef, {}))

    $bind_host = lookup('CONFIG_IP_VERSION') ? {
      'ipv6'  => '::0',
      default => '0.0.0.0',
      # TO-DO(mmagr): Add IPv6 support when hostnames are used
    }

    $admin_password = lookup('CONFIG_NOVA_KS_PW')

    class { 'nova::keystone::authtoken':
      password             => $admin_password,
      www_authenticate_uri => lookup('CONFIG_KEYSTONE_PUBLIC_URL_VERSIONLESS'),
      auth_url             => lookup('CONFIG_KEYSTONE_ADMIN_URL'),
    }

    if lookup('CONFIG_NOVA_PCI_ALIAS') == '' {
      $pci_alias = $facts['os_service_default']
    } else {
      $pci_alias = lookup('CONFIG_NOVA_PCI_ALIAS')
    }

    class { 'nova::pci':
      aliases => $pci_alias,
    }

    class { 'nova::api':
      api_bind_address           => $bind_host,
      enabled                    => true,
      sync_db                    => false,
      sync_db_api                => false,
      osapi_compute_workers      => lookup('CONFIG_SERVICE_WORKERS'),
      allow_resize_to_same_host  => lookup('CONFIG_NOVA_ALLOW_RESIZE_TO_SAME'),
      service_name               => 'httpd',
    }

    class { 'nova::metadata':
      neutron_metadata_proxy_shared_secret => lookup('CONFIG_NEUTRON_METADATA_PW_UNQUOTED', undef, undef, undef),
    }

    class { 'nova::wsgi::apache_api':
      bind_host => $bind_host,
      ssl       => false,
      workers   => lookup('CONFIG_SERVICE_WORKERS'),
    }

    class { 'nova::wsgi::apache_metadata':
      bind_host => $bind_host,
      ssl       => false,
      workers   => lookup('CONFIG_SERVICE_WORKERS'),
    }

    class { 'nova::db::sync':
      db_sync_timeout => 600,
    }

    class { 'nova::db::sync_api':
      db_sync_timeout => 600,
    }

    class { 'nova::placement':
      auth_url    => lookup('CONFIG_KEYSTONE_ADMIN_URL'),
      password    => $admin_password,
      region_name => lookup('CONFIG_KEYSTONE_REGION'),
    }

    $db_purge = lookup('CONFIG_NOVA_DB_PURGE_ENABLE')
    if $db_purge {
      class { 'nova::cron::archive_deleted_rows':
        hour        => '*/12',
        destination => '/dev/null',
      }
    }

    include nova::cell_v2::simple_setup

    $manage_flavors = str2bool(lookup('CONFIG_NOVA_MANAGE_FLAVORS'))
    if $manage_flavors {
      Class['::nova::api'] -> Nova_flavor<||>
      Class['::keystone'] -> Nova_flavor<||>

      nova_flavor { 'm1.tiny':
        ensure  => present,
        id      => '1',
        ram     => '512',
        disk    => '1',
        vcpus   => '1',
        require => [ Class['::nova::api'], Class['::nova::keystone::auth'] ],
      }

      nova_flavor { 'm1.small':
        ensure  => present,
        id      => '2',
        ram     => '2048',
        disk    => '20',
        vcpus   => '1',
        require => [ Class['::nova::api'], Class['::nova::keystone::auth'] ],
      }

      nova_flavor { 'm1.medium':
        ensure  => present,
        id      => '3',
        ram     => '4096',
        disk    => '40',
        vcpus   => '2',
        require => [ Class['::nova::api'], Class['::nova::keystone::auth'] ],
      }

      nova_flavor { 'm1.large':
        ensure  => present,
        id      => '4',
        ram     => '8192',
        disk    => '80',
        vcpus   => '4',
        require => [ Class['::nova::api'], Class['::nova::keystone::auth'] ],
      }

      nova_flavor { 'm1.xlarge':
        ensure  => present,
        id      => '5',
        ram     => '16384',
        disk    => '160',
        vcpus   => '8',
        require => [ Class['::nova::api'], Class['::nova::keystone::auth'] ],
      }
    }
}
