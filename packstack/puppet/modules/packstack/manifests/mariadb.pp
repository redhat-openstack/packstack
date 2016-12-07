class packstack::mariadb ()
{
  if hiera('CONFIG_MARIADB_INSTALL') == 'y' {
    create_resources(packstack::firewall, hiera('FIREWALL_MARIADB_RULES', {}))
    $max_connections = hiera('CONFIG_SERVICE_WORKERS') * 128

    if ($::mariadb_provides_galera) {
      # Since mariadb 10.1 galera is included in main mariadb
      $mariadb_package_name = 'mariadb-server-galera'
      $mariadb_present      = 'present'
    } else  {
      # Package mariadb-server conflicts with mariadb-galera-server
      $mariadb_package_name = 'mariadb-galera-server'
      $mariadb_present      = 'absent'
    }
    ensure_packages(['mariadb-server'], {'ensure' => $mariadb_present})

    $bind_address = hiera('CONFIG_IP_VERSION') ? {
      'ipv6'  => '::0',
      default => '0.0.0.0',
      # TO-DO(mmagr): Add IPv6 support when hostnames are used
    }

    $mysql_root_password = hiera('CONFIG_MARIADB_PW')

    class { '::mysql::server':
      package_name     => $mariadb_package_name,
      restart          => true,
      root_password    => $mysql_root_password,
      require          => Package['mariadb-server'],
      override_options => {
        'mysqld' => {
          'bind_address'           => $bind_address,
          'default_storage_engine' => 'InnoDB',
          'max_connections'        => $max_connections,
          'open_files_limit'       => '-1',
          # galera options
          'wsrep_provider'         => 'none',
          'wsrep_cluster_name'     => 'galera_cluster',
          'wsrep_sst_method'       => 'rsync',
          'wsrep_sst_auth'         => "root:${mysql_root_password}",
        },
      },
    }

    # deleting database users for security
    # this is done in mysql::server::account_security but has problems
    # when there is no fqdn, so we're defining a slightly different one here
    mysql_user { [ 'root@127.0.0.1', 'root@::1', '@localhost', '@%' ]:
      ensure  => 'absent',
      require => Class['mysql::server'],
    }

    if ($::fqdn != '' and $::fqdn != 'localhost') {
      mysql_user { [ "root@${::fqdn}", "@${::fqdn}"]:
        ensure  => 'absent',
        require => Class['mysql::server'],
      }
    }
    if ($::fqdn != $::hostname and $::hostname != 'localhost') {
      mysql_user { ["root@${::hostname}", "@${::hostname}"]:
        ensure  => 'absent',
        require => Class['mysql::server'],
      }
    }
  } else {
        class { '::remote::db': }
  }
}
