$bind_host = hiera('CONFIG_IP_VERSION') ? {
  'ipv6' => '::0',
  'ipv4' => '0.0.0.0',
}

class { '::neutron':
  bind_host             => $bind_host,
  rpc_backend           => 'neutron.openstack.common.rpc.impl_qpid',
  qpid_hostname         => hiera('CONFIG_AMQP_HOST_URL'),
  qpid_username         => hiera('CONFIG_AMQP_AUTH_USER'),
  qpid_password         => hiera('CONFIG_AMQP_AUTH_PASSWORD'),
  qpid_port             => hiera('CONFIG_AMQP_CLIENTS_PORT'),
  qpid_protocol         => hiera('CONFIG_AMQP_PROTOCOL'),
  core_plugin           => hiera('CONFIG_NEUTRON_CORE_PLUGIN'),
  allow_overlapping_ips => true,
  service_plugins       => hiera_array('SERVICE_PLUGINS'),
  verbose               => true,
  debug                 => hiera('CONFIG_DEBUG_MODE'),
}
