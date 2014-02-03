
class {"glance::api":
    auth_host => "%(CONFIG_KEYSTONE_HOST)s",
    keystone_tenant => "services",
    keystone_user => "glance",
    keystone_password => "%(CONFIG_GLANCE_KS_PW)s",
    pipeline => 'keystone',
    sql_connection => "mysql://glance:%(CONFIG_GLANCE_DB_PW)s@%(CONFIG_MYSQL_HOST)s/glance",
    verbose => true,
    debug => %(CONFIG_DEBUG_MODE)s,
}

class { 'glance::backend::file': }

class {"glance::registry":
    auth_host => "%(CONFIG_KEYSTONE_HOST)s",
    keystone_tenant => "services",
    keystone_user => "glance",
    keystone_password => "%(CONFIG_GLANCE_KS_PW)s",
    sql_connection => "mysql://glance:%(CONFIG_GLANCE_DB_PW)s@%(CONFIG_MYSQL_HOST)s/glance",
    verbose => true,
    debug => %(CONFIG_DEBUG_MODE)s,
}
