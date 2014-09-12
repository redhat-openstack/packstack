
# on EL6 we need to wait for innodb changes before starting mysqld
if $::operatingsystem in ['RedHat','CentOS','Scientific'] and $::operatingsystemmajrelease < 7 {
    $manage_service = false
    service { 'mysqld':
      enable  => true,
      ensure  => 'running',
      require => [ Package['mysql-server'], File['/etc/my.cnf'] ],
      before  => Exec['set_mysql_rootpw'],
    }
} else {
    $manage_service = true
}

class {"mysql::server":
    package_name     => "mariadb-galera-server",
    service_manage   => $manage_service,
    restart          => true,
    root_password    => "%(CONFIG_MARIADB_PW)s",
    override_options => {
      'mysqld' => { bind_address => "0.0.0.0",
                    default_storage_engine => "InnoDB",
                    max_connections => "1024",
                    open_files_limit => '-1',
      }
    }
}

include packstack::innodb

# deleting database users for security
# this is done in mysql::server::account_security but has problems
# when there is no fqdn, so we're defining a slightly different one here
database_user { [ 'root@127.0.0.1', 'root@::1', '@localhost', '@%%' ]:
    ensure  => 'absent', require => Class['mysql::server'],
}
if ($::fqdn != "" and $::fqdn != "localhost") {
    database_user { [ "root@${::fqdn}", "@${::fqdn}"]:
        ensure  => 'absent', require => Class['mysql::server'],
    }
}
if ($::fqdn != $::hostname and $::hostname != "localhost") {
    database_user { ["root@${::hostname}", "@${::hostname}"]:
        ensure  => 'absent', require => Class['mysql::server'],
    }
}
