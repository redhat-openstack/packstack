
class {"mysql::server":
    config_hash => {bind_address => "0.0.0.0",
                    root_password => "%(CONFIG_MYSQL_PW)s",}
}

# deleting database users for security
# this is done in mysql::server::account_security but has problems
# when there is no fqdn, so we're defining a slightly different one here
database_user { [ 'root@127.0.0.1', 'root@::1', '@localhost', '@%%' ]:
    ensure  => 'absent', require => Class['mysql::config'],
}
if ($::fqdn != "") {
    database_user { [ "root@${::fqdn}", "@${::fqdn}"]:
        ensure  => 'absent', require => Class['mysql::config'],
    }
}
if ($::fqdn != $::hostname) {
    database_user { ["root@${::hostname}", "@${::hostname}"]:
        ensure  => 'absent', require => Class['mysql::config'],
    }
}

class {"keystone::db::mysql":
    password      => "keystone_default_password",
    allowed_hosts => "%%",
}

class {"glance::db::mysql":
    password      => "glance_default_password",
    allowed_hosts => "%%",
}

class {"nova::db::mysql":
    password      => "nova_default_password",
    allowed_hosts => "%%",
}

class {"cinder::db::mysql":
    password      => "cinder_default_password",
    allowed_hosts => "%%",
}

firewall { '001 mysql incoming':
    proto    => 'tcp',
    dport    => ['3306'],
    action   => 'accept',
}
