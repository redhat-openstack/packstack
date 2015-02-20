$glance_ks_pw = hiera('CONFIG_GLANCE_DB_PW')
$glance_mariadb_host = hiera('CONFIG_MARIADB_HOST')
$glance_cfg_ctrl_host = hiera('CONFIG_CONTROLLER_HOST')

class { 'glance::api':
  auth_uri            => "http://${glance_cfg_ctrl_host}:5000/",
  identity_uri        => "http://${glance_cfg_ctrl_host}:35357/v2.0",
  keystone_tenant     => 'services',
  keystone_user       => 'glance',
  keystone_password   => hiera('CONFIG_GLANCE_KS_PW'),
  pipeline            => 'keystone',
  database_connection => "mysql://glance:${glance_ks_pw}@${glance_mariadb_host}/glance",
  verbose             => true,
  debug               => hiera('CONFIG_DEBUG_MODE'),
}

class { 'glance::registry':
  auth_uri            => "http://${glance_cfg_ctrl_host}:5000/",
  identity_uri        => "http://${glance_cfg_ctrl_host}:35357/v2.0",
  keystone_tenant     => 'services',
  keystone_user       => 'glance',
  keystone_password   => hiera('CONFIG_GLANCE_KS_PW'),
  database_connection => "mysql://glance:${glance_ks_pw}@${glance_mariadb_host}/glance",
  verbose             => true,
  debug               => hiera('CONFIG_DEBUG_MODE'),
}

