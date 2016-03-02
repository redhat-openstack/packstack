$glance_ks_pw = hiera('CONFIG_GLANCE_DB_PW')
$glance_mariadb_host = hiera('CONFIG_MARIADB_HOST_URL')
$glance_cfg_ctrl_host = hiera('CONFIG_KEYSTONE_HOST_URL')

# glance option bind_host requires address without brackets
$bind_host = hiera('CONFIG_IP_VERSION') ? {
  'ipv6'  => '::0',
  default => '0.0.0.0',
  # TO-DO(mmagr): Add IPv6 support when hostnames are used
}
# magical hack for magical config - glance option registry_host requires brackets
$registry_host = hiera('CONFIG_IP_VERSION') ? {
  'ipv6'  => '[::0]',
  default => '0.0.0.0',
  # TO-DO(mmagr): Add IPv6 support when hostnames are used
}

class { '::glance::api':
  bind_host           => $bind_host,
  registry_host       => $registry_host,
  auth_uri            => hiera('CONFIG_KEYSTONE_PUBLIC_URL'),
  identity_uri        => hiera('CONFIG_KEYSTONE_ADMIN_URL'),
  keystone_tenant     => 'services',
  keystone_user       => 'glance',
  keystone_password   => hiera('CONFIG_GLANCE_KS_PW'),
  pipeline            => 'keystone',
  database_connection => "mysql+pymysql://glance:${glance_ks_pw}@${glance_mariadb_host}/glance",
  verbose             => true,
  debug               => hiera('CONFIG_DEBUG_MODE'),
  os_region_name      => hiera('CONFIG_KEYSTONE_REGION'),
  workers             => $service_workers,
  known_stores        => ['file', 'http', 'swift']
}

class { '::glance::registry':
  auth_uri            => hiera('CONFIG_KEYSTONE_PUBLIC_URL'),
  identity_uri        => hiera('CONFIG_KEYSTONE_ADMIN_URL'),
  bind_host           => $bind_host,
  keystone_tenant     => 'services',
  keystone_user       => 'glance',
  keystone_password   => hiera('CONFIG_GLANCE_KS_PW'),
  database_connection => "mysql+pymysql://glance:${glance_ks_pw}@${glance_mariadb_host}/glance",
  verbose             => true,
  debug               => hiera('CONFIG_DEBUG_MODE'),
  workers             => $service_workers
}
