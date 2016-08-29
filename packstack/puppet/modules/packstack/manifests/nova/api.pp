class packstack::nova::api ()
{
    create_resources(packstack::firewall, hiera('FIREWALL_NOVA_API_RULES', {}))

    require 'keystone::python'
    $bind_host = hiera('CONFIG_IP_VERSION') ? {
      'ipv6'  => '::0',
      default => '0.0.0.0',
      # TO-DO(mmagr): Add IPv6 support when hostnames are used
    }

    $config_use_neutron = hiera('CONFIG_NEUTRON_INSTALL')
    if $config_use_neutron == 'y' {
        $default_floating_pool = 'public'
    } else {
        $default_floating_pool = 'nova'
    }

    $auth_uri = hiera('CONFIG_KEYSTONE_PUBLIC_URL')
    $admin_password = hiera('CONFIG_NOVA_KS_PW')

    class {'::nova::keystone::authtoken':
      password => $admin_password,
      auth_uri => $auth_uri,
      auth_url => hiera('CONFIG_KEYSTONE_ADMIN_URL'),
    }

    class { '::nova::api':
      api_bind_address                     => $bind_host,
      metadata_listen                      => $bind_host,
      enabled                              => true,
      neutron_metadata_proxy_shared_secret => hiera('CONFIG_NEUTRON_METADATA_PW_UNQUOTED', undef),
      default_floating_pool                => $default_floating_pool,
      pci_alias                            => hiera('CONFIG_NOVA_PCI_ALIAS'),
      sync_db_api                          => true,
      osapi_compute_workers                => hiera('CONFIG_SERVICE_WORKERS'),
      metadata_workers                     => hiera('CONFIG_SERVICE_WORKERS'),
    }

    Package<| title == 'nova-common' |> -> Class['nova::api']

    $db_purge = hiera('CONFIG_NOVA_DB_PURGE_ENABLE')
    if $db_purge {
      class { '::nova::cron::archive_deleted_rows':
        hour        => '*/12',
        destination => '/dev/null',
      }
    }

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
