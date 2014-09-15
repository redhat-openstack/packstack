
# Package mariadb-server conflicts with mariadb-galera-server
package { 'mariadb-server':
  ensure => absent,
}

$bind_address = hiera('CONFIG_IP_VERSION') ? {
  'ipv6'  => '::0',
  default => '0.0.0.0',
  # TO-DO(mmagr): Add IPv6 support when hostnames are used
}

# hack around galera packaging issue, they are duplicating
# bind-address config option in galera.cnf
class { '::galera::server':
  wsrep_bind_address    => $bind_address,
  manage_service        => false,
  wsrep_provider        => 'none',
  create_mysql_resource => false,
}

class { '::mysql::server':
  package_name     => 'mariadb-galera-server',
  restart          => true,
  root_password    => hiera('CONFIG_MARIADB_PW'),
  require          => Package['mariadb-server'],
  override_options => {
    'mysqld' => { bind_address           => $bind_address,
                  default_storage_engine => 'InnoDB',
                  max_connections        => '1024',
                  open_files_limit       => '-1',
    },
  },
}

# deleting database users for security
# this is done in mysql::server::account_security but has problems
# when there is no fqdn, so we're defining a slightly different one here
mysql_user { [ 'root@127.0.0.1', 'root@::1', '@localhost', '@%%' ]:
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
