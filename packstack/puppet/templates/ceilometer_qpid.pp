class { 'ceilometer':
  metering_secret => hiera('CONFIG_CEILOMETER_SECRET'),
  qpid_hostname   => hiera('CONFIG_AMQP_HOST'),
  qpid_username   => hiera('CONFIG_AMQP_AUTH_USER'),
  qpid_password   => hiera('CONFIG_AMQP_AUTH_PASSWORD'),
  rpc_backend     => 'ceilometer.openstack.common.rpc.impl_qpid',
  verbose         => true,
  debug           => hiera('CONFIG_DEBUG_MODE'),
  qpid_port       => hiera('CONFIG_AMQP_CLIENTS_PORT'),
  qpid_protocol   => hiera('CONFIG_AMQP_PROTOCOL'),
}
