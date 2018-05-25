class packstack::nova::api ()
{
    create_resources(packstack::firewall, hiera('FIREWALL_NOVA_API_RULES', {}))

    $bind_host = hiera('CONFIG_IP_VERSION') ? {
      'ipv6'  => '::0',
      default => '0.0.0.0',
      # TO-DO(mmagr): Add IPv6 support when hostnames are used
    }

    $auth_uri = hiera('CONFIG_KEYSTONE_PUBLIC_URL_VERSIONLESS')
    $admin_password = hiera('CONFIG_NOVA_KS_PW')

    class {'::nova::keystone::authtoken':
      password => $admin_password,
      auth_uri => $auth_uri,
      auth_url => hiera('CONFIG_KEYSTONE_ADMIN_URL'),
    }

    if hiera('CONFIG_NOVA_PCI_ALIAS') == '' {
      $pci_alias = $::os_service_default
    } else {
      $pci_alias = hiera('CONFIG_NOVA_PCI_ALIAS')
    }

    class { '::nova::api':
      api_bind_address                     => $bind_host,
      metadata_listen                      => $bind_host,
      enabled                              => true,
      neutron_metadata_proxy_shared_secret => hiera('CONFIG_NEUTRON_METADATA_PW_UNQUOTED', undef),
      sync_db_api                          => true,
      osapi_compute_workers                => hiera('CONFIG_SERVICE_WORKERS'),
      metadata_workers                     => hiera('CONFIG_SERVICE_WORKERS'),
      allow_resize_to_same_host            => hiera('CONFIG_NOVA_ALLOW_RESIZE_TO_SAME'),
    }

    class { '::nova::pci':
      aliases                              => $pci_alias,
    }

    class { '::nova::wsgi::apache_placement':
      bind_host => $bind_host,
      api_port  => '8778',
      ssl       => false,
      workers   => hiera('CONFIG_SERVICE_WORKERS'),
    }

    class { '::nova::placement':
      auth_url       => $auth_uri,
      password       => $admin_password,
      os_region_name => hiera('CONFIG_KEYSTONE_REGION'),
    }

    $db_purge = hiera('CONFIG_NOVA_DB_PURGE_ENABLE')
    if $db_purge {
      class { '::nova::cron::archive_deleted_rows':
        hour        => '*/12',
        destination => '/dev/null',
      }
    }

    include ::nova::cell_v2::simple_setup

    $manage_flavors = str2bool(hiera('CONFIG_NOVA_MANAGE_FLAVORS'))
    if $manage_flavors {
      Class['::nova::api'] -> Nova_flavor<||>
      Class['::keystone'] -> Nova_flavor<||>

      nova_flavor { 'm1.tiny':
        ensure => present,
        id     => '1',
        ram    => '512',
        disk   => '1',
        vcpus  => '1',
        require => [ Class['::nova::api'], Class['::nova::keystone::auth'] ],
      }

      nova_flavor { 'm1.small':
        ensure => present,
        id     => '2',
        ram    => '2048',
        disk   => '20',
        vcpus  => '1',
        require => [ Class['::nova::api'], Class['::nova::keystone::auth'] ],
      }

      nova_flavor { 'm1.medium':
        ensure => present,
        id     => '3',
        ram    => '4096',
        disk   => '40',
        vcpus  => '2',
        require => [ Class['::nova::api'], Class['::nova::keystone::auth'] ],
      }

      nova_flavor { 'm1.large':
        ensure => present,
        id     => '4',
        ram    => '8192',
        disk   => '80',
        vcpus  => '4',
        require => [ Class['::nova::api'], Class['::nova::keystone::auth'] ],
      }

      nova_flavor { 'm1.xlarge':
        ensure => present,
        id     => '5',
        ram    => '16384',
        disk   => '160',
        vcpus  => '8',
        require => [ Class['::nova::api'], Class['::nova::keystone::auth'] ],
      }
    }
}
