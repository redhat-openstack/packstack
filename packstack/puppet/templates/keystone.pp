$keystone_use_ssl = false
$keystone_service_name = hiera('CONFIG_KEYSTONE_SERVICE_NAME')
$keystone_cfg_ks_db_pw = hiera('CONFIG_KEYSTONE_DB_PW')
$keystone_cfg_mariadb_host = hiera('CONFIG_MARIADB_HOST')
$keystone_endpoint_cfg_ctrl_host = hiera('CONFIG_CONTROLLER_HOST')

class { 'keystone':
  admin_token         => hiera('CONFIG_KEYSTONE_ADMIN_TOKEN'),
  database_connection => "mysql://keystone_admin:${keystone_cfg_ks_db_pw}@${keystone_cfg_mariadb_host}/keystone",
  token_format        => hiera('CONFIG_KEYSTONE_TOKEN_FORMAT'),
  verbose             => true,
  debug               => hiera('CONFIG_DEBUG_MODE'),
  service_name        => $keystone_service_name,
  enable_ssl          => $keystone_use_ssl,
}

if $keystone_service_name == 'httpd' {
  include packstack::apache_common

  class { 'keystone::wsgi::apache':
    ssl => $keystone_use_ssl,
  }
}

class { 'keystone::roles::admin':
  email        => 'root@localhost',
  password     => hiera('CONFIG_KEYSTONE_ADMIN_PW'),
  admin_tenant => 'admin',
}

class { 'keystone::endpoint':
  public_url   => "http://${keystone_endpoint_cfg_ctrl_host}:5000",
  internal_url => "http://${keystone_endpoint_cfg_ctrl_host}:5000",
  admin_url    => "http://${keystone_endpoint_cfg_ctrl_host}:35357",
  region       => hiera('CONFIG_KEYSTONE_REGION'),
}

# Run token flush every minute (without output so we won't spam admins)
cron { 'token-flush':
  ensure  => 'present',
  command => '/usr/bin/keystone-manage token_flush >/dev/null 2>&1',
  minute  => '*/1',
  user    => 'keystone',
  require => [User['keystone'], Group['keystone']],
} ->
service { 'crond':
  ensure => 'running',
  enable => true,
}

