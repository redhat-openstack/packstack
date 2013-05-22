

class {"glance::api":
    auth_host => "%(CONFIG_KEYSTONE_HOST)s",
    keystone_tenant => "services",
    keystone_user => "glance",
    keystone_password => "%(CONFIG_GLANCE_KS_PW)s",
    pipeline => 'keystone',
    sql_connection => "mysql://glance:%(CONFIG_GLANCE_DB_PW)s@%(CONFIG_MYSQL_HOST)s/glance"
}

class { 'glance::backend::file': }

class {"glance::registry":
    auth_host => "%(CONFIG_KEYSTONE_HOST)s",
    keystone_tenant => "services",
    keystone_user => "glance",
    keystone_password => "%(CONFIG_GLANCE_KS_PW)s",
    sql_connection => "mysql://glance:%(CONFIG_GLANCE_DB_PW)s@%(CONFIG_MYSQL_HOST)s/glance"
}

firewall { '001 glance incoming':
    proto    => 'tcp',
    dport    => ['9292'],
    action   => 'accept',
}
