
class { 'neutron':
  rabbit_host           => '%(CONFIG_AMQP_HOST)s',
  rabbit_port           => '%(CONFIG_AMQP_CLIENTS_PORT)s',
  rabbit_use_ssl        => %(CONFIG_AMQP_ENABLE_SSL)s,
  rabbit_user           => '%(CONFIG_AMQP_AUTH_USER)s',
  rabbit_password       => '%(CONFIG_AMQP_AUTH_PASSWORD)s',
  core_plugin           => '%(CONFIG_NEUTRON_CORE_PLUGIN)s',
  allow_overlapping_ips => true,
  service_plugins       => %(SERVICE_PLUGINS)s,
  verbose               => true,
  debug                 => %(CONFIG_DEBUG_MODE)s,
}
