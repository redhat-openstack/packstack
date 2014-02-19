
class { 'neutron':
  rpc_backend           => 'neutron.openstack.common.rpc.impl_qpid',
  qpid_hostname         => '%(CONFIG_AMQP_HOST)s',
  qpid_username         => '%(CONFIG_AMQP_AUTH_USER)s',
  qpid_password         => '%(CONFIG_AMQP_AUTH_PASSWORD)s',
  qpid_port             => '%(CONFIG_AMQP_CLIENTS_PORT)s',
  qpid_protocol         => '%(CONFIG_AMQP_PROTOCOL)s',
  core_plugin           => '%(CONFIG_NEUTRON_CORE_PLUGIN)s',
  allow_overlapping_ips => true,
  service_plugins       => %(SERVICE_PLUGINS)s,
  verbose               => true,
  debug                 => %(CONFIG_DEBUG_MODE)s,
}
