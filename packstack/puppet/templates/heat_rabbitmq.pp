$heat_rabbitmq_cfg_ctrl_host = hiera('CONFIG_KEYSTONE_HOST_URL')
$heat_rabbitmq_cfg_heat_db_pw = hiera('CONFIG_HEAT_DB_PW')
$heat_rabbitmq_cfg_mariadb_host = hiera('CONFIG_MARIADB_HOST_URL')

class { '::heat':
  keystone_host       => $heat_rabbitmq_cfg_ctrl_host,
  keystone_password   => hiera('CONFIG_HEAT_KS_PW'),
  auth_uri            => "http://${heat_rabbitmq_cfg_ctrl_host}:35357/v2.0",
  keystone_ec2_uri    => "http://${heat_rabbitmq_cfg_ctrl_host}:35357/v2.0",
  rpc_backend         => 'heat.openstack.common.rpc.impl_kombu',
  rabbit_host         => hiera('CONFIG_AMQP_HOST_URL'),
  rabbit_port         => hiera('CONFIG_AMQP_CLIENTS_PORT'),
  rabbit_use_ssl      => hiera('CONFIG_AMQP_ENABLE_SSL'),
  rabbit_userid       => hiera('CONFIG_AMQP_AUTH_USER'),
  rabbit_password     => hiera('CONFIG_AMQP_AUTH_PASSWORD'),
  verbose             => true,
  debug               => hiera('CONFIG_DEBUG_MODE'),
  database_connection => "mysql://heat:${heat_rabbitmq_cfg_heat_db_pw}@${heat_rabbitmq_cfg_mariadb_host}/heat",
}
