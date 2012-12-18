class {"keystone":
    admin_token => "%(CONFIG_KEYSTONE_ADMINTOKEN)s",
    sql_connection => "mysql://keystone_admin:keystone_default_password@%(CONFIG_MYSQL_HOST)s/keystone",
}

class {"keystone::roles::admin":
    email => "test@test.com",
    password => "%(CONFIG_KEYSTONE_ADMINPASSWD)s",
    admin_tenant => "admin"
}

class {"openstack::auth_file":
    admin_password => "%(CONFIG_KEYSTONE_ADMINPASSWD)s",
    admin_tenant => "admin",
    keystone_admin_token => "%(CONFIG_KEYSTONE_ADMINTOKEN)s"
}

class {"keystone::endpoint":
    public_address  => "%(CONFIG_KEYSTONE_HOST)s",
    admin_address  => "%(CONFIG_KEYSTONE_HOST)s",
    internal_address  => "%(CONFIG_KEYSTONE_HOST)s",
}

firewall { '001 keystone incoming':
    proto    => 'tcp',
    dport    => ['5000', '35357'],
    action   => 'accept',
}

