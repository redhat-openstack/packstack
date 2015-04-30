$heat_qpid_cfg_heat_db_pw = hiera('CONFIG_HEAT_DB_PW')
$heat_qpid_cfg_mariadb_host = hiera('CONFIG_MARIADB_HOST_URL')

class { '::heat':
  keystone_password   => hiera('CONFIG_HEAT_KS_PW'),
  auth_uri            => hiera('CONFIG_KEYSTONE_PUBLIC_URL'),
  identity_uri        => hiera('CONFIG_KEYSTONE_ADMIN_URL'),
  keystone_ec2_uri    => hiera('CONFIG_KEYSTONE_PUBLIC_URL'),
  rpc_backend         => 'heat.openstack.common.rpc.impl_qpid',
  qpid_hostname       => hiera('CONFIG_AMQP_HOST_URL'),
  qpid_username       => hiera('CONFIG_AMQP_AUTH_USER'),
  qpid_password       => hiera('CONFIG_AMQP_AUTH_PASSWORD'),
  qpid_port           => hiera('CONFIG_AMQP_CLIENTS_PORT'),
  qpid_protocol       => hiera('CONFIG_AMQP_PROTOCOL'),
  verbose             => true,
  debug               => hiera('CONFIG_DEBUG_MODE'),
  database_connection => "mysql://heat:${heat_qpid_cfg_heat_db_pw}@${heat_qpid_cfg_mariadb_host}/heat",
}
