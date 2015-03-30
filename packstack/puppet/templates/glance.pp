$glance_ks_pw = hiera('CONFIG_GLANCE_DB_PW')
$glance_mariadb_host = hiera('CONFIG_MARIADB_HOST_URL')
$glance_cfg_ctrl_host = hiera('CONFIG_KEYSTONE_HOST_URL')

# glance option bind_host requires address without brackets
$bind_host = hiera('CONFIG_IP_VERSION') ? {
  'ipv6' => '::0',
  'ipv4' => '0.0.0.0',
}
# magical hack for magical config - glance option registry_host requires brackets
$registry_host = hiera('CONFIG_IP_VERSION') ? {
  'ipv6' => '[::0]',
  'ipv4' => '0.0.0.0',
}

class { '::glance::api':
  bind_host           => $bind_host,
  registry_host       => $registry_host,
  auth_uri            => "http://${glance_cfg_ctrl_host}:5000/",
  identity_uri        => "http://${glance_cfg_ctrl_host}:35357",
  keystone_tenant     => 'services',
  keystone_user       => 'glance',
  keystone_password   => hiera('CONFIG_GLANCE_KS_PW'),
  pipeline            => 'keystone',
  database_connection => "mysql://glance:${glance_ks_pw}@${glance_mariadb_host}/glance",
  verbose             => true,
  debug               => hiera('CONFIG_DEBUG_MODE'),
  os_region_name      => hiera('CONFIG_KEYSTONE_REGION'),
}

class { '::glance::registry':
  auth_uri            => "http://${glance_cfg_ctrl_host}:5000/",
  identity_uri        => "http://${glance_cfg_ctrl_host}:35357",
  bind_host           => $bind_host,
  keystone_tenant     => 'services',
  keystone_user       => 'glance',
  keystone_password   => hiera('CONFIG_GLANCE_KS_PW'),
  database_connection => "mysql://glance:${glance_ks_pw}@${glance_mariadb_host}/glance",
  verbose             => true,
  debug               => hiera('CONFIG_DEBUG_MODE'),
}
