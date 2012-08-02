

class {"glance::api":
    auth_host => "%(CONFIG_KEYSTONE_HOST)s",
    keystone_tenant => "services",
    keystone_user => "glance",
    keystone_password => "glance_password",
}

class { 'glance::backend::file': }

class {"glance::registry":
    auth_host => "%(CONFIG_KEYSTONE_HOST)s",
    keystone_tenant => "services",
    keystone_user => "glance",
    keystone_password => "glance_password",
    sql_connection => "mysql://glance:glance_default_password@%(CONFIG_MYSQL_HOST)s/glance"
}

firewall { '001 glance incomming':
    proto    => 'tcp',
    dport    => ['9292'],
    action   => 'accept',
}

