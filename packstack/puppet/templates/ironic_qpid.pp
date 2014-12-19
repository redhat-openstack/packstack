$ironic_qpid_cfg_ironic_db_pw = hiera('CONFIG_IRONIC_DB_PW')
$ironic_qpid_cfg_mariadb_host = hiera('CONFIG_MARIADB_HOST')

class { 'ironic':
  rpc_backend         => 'ironic.openstack.common.rpc.impl_qpid',
  qpid_hostname       => hiera('CONFIG_AMQP_HOST'),
  qpid_port           => hiera('CONFIG_AMQP_CLIENTS_PORT'),
  qpid_protocol       => hiera('CONFIG_AMQP_PROTOCOL'),
  qpid_username       => hiera('CONFIG_AMQP_AUTH_USER'),
  qpid_password       => hiera('CONFIG_AMQP_AUTH_PASSWORD'),
  database_connection => "mysql://ironic:${ironic_qpid_cfg_ironic_db_pw}@${ironic_qpid_cfg_mariadb_host}/ironic",
  debug               => true,
  verbose             => true,
}
