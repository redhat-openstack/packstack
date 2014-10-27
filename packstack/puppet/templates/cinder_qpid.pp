$cinder_qpid_cfg_cinder_db_pw = hiera('CONFIG_CINDER_DB_PW')
$cinder_qpid_cfg_mariadb_host = hiera('CONFIG_MARIADB_HOST')

class {'cinder':
  rpc_backend         => 'cinder.openstack.common.rpc.impl_qpid',
  qpid_hostname       => hiera('CONFIG_AMQP_HOST'),
  qpid_port           => hiera('CONFIG_AMQP_CLIENTS_PORT'),
  qpid_protocol       => hiera('CONFIG_AMQP_PROTOCOL'),
  qpid_username       => hiera('CONFIG_AMQP_AUTH_USER'),
  qpid_password       => hiera('CONFIG_AMQP_AUTH_PASSWORD'),
  database_connection => "mysql://cinder:${cinder_qpid_cfg_cinder_db_pw}@${cinder_qpid_cfg_mariadb_host}/cinder",
  verbose             => true,
  debug               => hiera('CONFIG_DEBUG_MODE'),
}
