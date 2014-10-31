$heat_qpid_cfg_ctrl_host = hiera('CONFIG_CONTROLLER_HOST')
$heat_qpid_cfg_heat_db_pw = hiera('CONFIG_HEAT_DB_PW')
$heat_qpid_cfg_mariadb_host = hiera('CONFIG_MARIADB_HOST')

class { 'heat':
  keystone_host       => $heat_cfn_cfg_ctrl_host,
  keystone_password   => hiera('CONFIG_HEAT_KS_PW'),
  auth_uri            => "http://${heat_qpid_cfg_ctrl_host}:35357/v2.0",
  keystone_ec2_uri    => "http://${heat_qpid_cfg_ctrl_host}:35357/v2.0",
  rpc_backend         => 'heat.openstack.common.rpc.impl_qpid',
  qpid_hostname       => hiera('CONFIG_AMQP_HOST'),
  qpid_username       => hiera('CONFIG_AMQP_AUTH_USER'),
  qpid_password       => hiera('CONFIG_AMQP_AUTH_PASSWORD'),
  qpid_port           => hiera('CONFIG_AMQP_CLIENTS_PORT'),
  qpid_protocol       => hiera('CONFIG_AMQP_PROTOCOL'),
  verbose             => true,
  debug               => hiera('CONFIG_DEBUG_MODE'),
  database_connection => "mysql://heat:${heat_qpid_cfg_heat_db_pw}@${heat_qpid_cfg_mariadb_host}/heat",
}
