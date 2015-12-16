$sahara_cfg_sahara_db_pw = hiera('CONFIG_SAHARA_DB_PW')
$sahara_cfg_sahara_mariadb_host = hiera('CONFIG_MARIADB_HOST_URL')
$sahara_cfg_config_neutron_install = hiera('CONFIG_NEUTRON_INSTALL')

class { '::sahara':
  database_connection =>
    "mysql+pymysql://sahara:${sahara_cfg_sahara_db_pw}@${sahara_cfg_sahara_mariadb_host}/sahara",
  verbose             => true,
  debug               => hiera('CONFIG_DEBUG_MODE'),
  admin_user          => 'sahara',
  admin_password      => hiera('CONFIG_SAHARA_KS_PW'),
  admin_tenant_name   => 'services',
  auth_uri            => hiera('CONFIG_KEYSTONE_PUBLIC_URL'),
  identity_uri        => hiera('CONFIG_KEYSTONE_ADMIN_URL'),
  use_neutron         => ($sahara_cfg_config_neutron_install == 'y'),
  host                => hiera('CONFIG_SAHARA_HOST'),
  rpc_backend         => 'qpid',
  qpid_hostname       => hiera('CONFIG_AMQP_HOST_URL'),
  qpid_port           => hiera('CONFIG_AMQP_CLIENTS_PORT'),
  qpid_protocol       => hiera('CONFIG_AMQP_PROTOCOL'),
  qpid_username       => hiera('CONFIG_AMQP_AUTH_USER'),
  qpid_password       => hiera('CONFIG_AMQP_AUTH_PASSWORD'),
}
