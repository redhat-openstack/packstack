$sahara_cfg_sahara_db_pw = hiera('CONFIG_SAHARA_DB_PW')
$sahara_cfg_sahara_mariadb_host = hiera('CONFIG_MARIADB_HOST_URL')

$sahara_cfg_config_neutron_install = hiera('CONFIG_NEUTRON_INSTALL')

class { '::sahara':
  database_connection =>
    "mysql://sahara:${sahara_cfg_sahara_db_pw}@${sahara_cfg_sahara_mariadb_host}/sahara",
  verbose             => true,
  debug               => hiera('CONFIG_DEBUG_MODE'),
  keystone_username   => 'sahara',
  keystone_password    => hiera('CONFIG_SAHARA_KS_PW'),
  keystone_tenant     => 'services',
  keystone_url        => hiera('CONFIG_KEYSTONE_PUBLIC_URL'),
  identity_url        => hiera('CONFIG_KEYSTONE_ADMIN_URL'),
  use_neutron         => ($sahara_cfg_config_neutron_install == 'y'),
  service_host        => hiera('CONFIG_SAHARA_HOST'),
}
