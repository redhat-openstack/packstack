$bind_host = hiera('CONFIG_IP_VERSION') ? {
  'ipv6' => '::0',
  'ipv4' => '0.0.0.0',
}

class { '::neutron':
  bind_host             => $bind_host,
  rabbit_host           => hiera('CONFIG_AMQP_HOST_URL'),
  rabbit_port           => hiera('CONFIG_AMQP_CLIENTS_PORT'),
  rabbit_use_ssl        => hiera('CONFIG_AMQP_ENABLE_SSL'),
  rabbit_user           => hiera('CONFIG_AMQP_AUTH_USER'),
  rabbit_password       => hiera('CONFIG_AMQP_AUTH_PASSWORD'),
  core_plugin           => hiera('CONFIG_NEUTRON_CORE_PLUGIN'),
  allow_overlapping_ips => true,
  service_plugins       => hiera_array('SERVICE_PLUGINS'),
  verbose               => true,
  debug                 => hiera('CONFIG_DEBUG_MODE'),
}
