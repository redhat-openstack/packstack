$gnocchi_cfg_db_pw = hiera('CONFIG_GNOCCHI_DB_PW')
$gnocchi_cfg_mariadb_host = hiera('CONFIG_MARIADB_HOST_URL')

class { '::apache':
  purge_configs => false,
}

class { '::gnocchi::wsgi::apache':
  workers => $service_workers,
  ssl     => false
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

class { '::gnocchi::db::sync': 
  extra_opts => '--create-legacy-resource-types',
}
class { '::gnocchi::storage': }
class { '::gnocchi::storage::file': }

class {'::gnocchi::metricd': }

class {'::gnocchi::statsd':
  resource_id         => '5e3fcbe2-7aab-475d-b42c-a440aa42e5ad',
  user_id             => 'e0ca4711-1128-422c-abd6-62db246c32e7',
  project_id          => 'af0c88e8-90d8-4795-9efe-57f965e67318',
  archive_policy_name => 'high',
  flush_delay         => '10',
}

include ::gnocchi::client
