$gnocchi_cfg_db_pw = hiera('CONFIG_GNOCCHI_DB_PW')
$gnocchi_cfg_mariadb_host = hiera('CONFIG_MARIADB_HOST_URL')

class { '::apache':
  purge_configs => false,
}

class { '::gnocchi::wsgi::apache':
  workers => $service_workers,
  ssl     => false
}
if hiera('CONFIG_KEYSTONE_SERVICE_NAME') == 'httpd' {
  apache::listen { '5000': }
  apache::listen { '35357': }
}

class { '::gnocchi':
  database_connection => "mysql+pymysql://gnocchi:${gnocchi_cfg_db_pw}@${gnocchi_cfg_mariadb_host}/gnocchi?charset=utf8",
}

$bind_host = hiera('CONFIG_IP_VERSION') ? {
 'ipv6'  => '::0',
 default => '0.0.0.0',
}

class { '::gnocchi::api':
  host                   => $bind_host,
  keystone_identity_uri  => hiera('CONFIG_KEYSTONE_ADMIN_URL'),
  keystone_password      => hiera('CONFIG_GNOCCHI_KS_PW'),
  keystone_auth_uri      => hiera('CONFIG_KEYSTONE_PUBLIC_URL'),
  service_name           => 'httpd',
}

# TO-DO: Remove this workaround as soon as module support is implemented (see rhbz#1300662)
gnocchi_config {
  'keystone_authtoken/auth_version': value => hiera('CONFIG_KEYSTONE_API_VERSION');
}

class { '::gnocchi::db::sync': }
class { '::gnocchi::storage': }
class { '::gnocchi::storage::file': }

class {'::gnocchi::metricd': }

include ::gnocchi::client
