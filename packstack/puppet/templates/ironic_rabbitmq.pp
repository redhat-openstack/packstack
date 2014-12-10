$ironic_rabbitmq_cfg_ironic_db_pw = hiera('CONFIG_IRONIC_DB_PW')
$ironic_rabbitmq_cfg_mariadb_host = hiera('CONFIG_MARIADB_HOST')

class { 'ironic':
  rpc_backend         => 'ironic.openstack.common.rpc.impl_kombu',
  rabbit_host         => hiera('CONFIG_AMQP_HOST'),
  rabbit_port         => hiera('CONFIG_AMQP_CLIENTS_PORT'),
  rabbit_user         => hiera('CONFIG_AMQP_AUTH_USER'),
  rabbit_password     => hiera('CONFIG_AMQP_AUTH_PASSWORD'),
  database_connection => "mysql://ironic:${ironic_rabbitmq_cfg_ironic_db_pw}@${ironic_rabbitmq_cfg_mariadb_host}/ironic",
  debug               => true,
  verbose             => true,
}
