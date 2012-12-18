
class {"mysql::server":
    config_hash => {bind_address => "0.0.0.0",
                    root_password => "%(CONFIG_MYSQL_PW)s",}
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
