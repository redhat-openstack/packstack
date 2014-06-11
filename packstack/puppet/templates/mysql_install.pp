
# on EL6 we need to wait for innodb changes before starting mysqld
if $::operatingsystem in ['RedHat','Centos','Scientific'] and $::operatingsystemrelease < 7 {
    $manage_service = false
    service { 'mysqld':
      enable  => true,
      ensure  => 'running',
      require => [ Package['mysql-server'], File['/etc/my.cnf'] ],
      before  => Exec['set_mysql_rootpw'],
    }
    $includedir = '/etc/mysql/conf.d'
} else {
    $manage_service = true
    $includedir = '/etc/my.cnf.d'
}

class {"mysql::server":
    manage_service => $manage_service,
    config_hash => {bind_address => "0.0.0.0",
                    default_engine => "InnoDB",
                    root_password => "%(CONFIG_MYSQL_PW)s",}
}

class { "packstack::innodb":
    includedir => "$includedir",
}

# deleting database users for security
# this is done in mysql::server::account_security but has problems
# when there is no fqdn, so we're defining a slightly different one here
database_user { [ 'root@127.0.0.1', 'root@::1', '@localhost', '@%%' ]:
    ensure  => 'absent', require => Class['mysql::config'],
}
if ($::fqdn != "" and $::fqdn != "localhost") {
    database_user { [ "root@${::fqdn}", "@${::fqdn}"]:
        ensure  => 'absent', require => Class['mysql::config'],
    }
}
if ($::fqdn != $::hostname and $::hostname != "localhost") {
    database_user { ["root@${::hostname}", "@${::hostname}"]:
        ensure  => 'absent', require => Class['mysql::config'],
    }
}
