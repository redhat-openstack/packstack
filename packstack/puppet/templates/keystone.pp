$keystone_use_ssl = false

class {"keystone":
    admin_token => "%(CONFIG_KEYSTONE_ADMIN_TOKEN)s",
    sql_connection => "mysql://keystone_admin:%(CONFIG_KEYSTONE_DB_PW)s@%(CONFIG_MARIADB_HOST)s/keystone",
    token_format => "%(CONFIG_KEYSTONE_TOKEN_FORMAT)s",
    verbose => true,
    debug => %(CONFIG_DEBUG_MODE)s,
    mysql_module => '2.2',
    service_name => '%(CONFIG_KEYSTONE_SERVICE_NAME)s',
    enable_ssl => $keystone_use_ssl,
}

if '%(CONFIG_KEYSTONE_SERVICE_NAME)s' == 'httpd' {
  include packstack::apache_common
  class {"keystone::wsgi::apache":
    ssl => $keystone_use_ssl,
  }
}

class {"keystone::roles::admin":
    email => "root@localhost",
    password => "%(CONFIG_KEYSTONE_ADMIN_PW)s",
    admin_tenant => "admin"
}

class {"keystone::endpoint":
    region => "%(CONFIG_KEYSTONE_REGION)s",
    public_address  => "%(CONFIG_CONTROLLER_HOST)s",
    admin_address  => "%(CONFIG_CONTROLLER_HOST)s",
    internal_address  => "%(CONFIG_CONTROLLER_HOST)s",
}

# Run token flush every minute (without output so we won't spam admins)
cron { 'token-flush':
    ensure => 'present',
    command => '/usr/bin/keystone-manage token_flush >/dev/null 2>&1',
    minute => '*/1',
    user => 'keystone',
    require => [User['keystone'], Group['keystone']],
} -> service { 'crond':
    ensure => 'running',
    enable => true,
}
