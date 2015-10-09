$bind_host = hiera('CONFIG_IP_VERSION') ? {
  'ipv6'  => '::0',
  default => '0.0.0.0',
  # TO-DO(mmagr): Add IPv6 support when hostnames are used
}

class { '::neutron':
  bind_host             => $bind_host,
  rpc_backend           => 'qpid',
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
