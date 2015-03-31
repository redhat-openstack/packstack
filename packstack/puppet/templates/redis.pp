$redis_port = hiera('CONFIG_REDIS_PORT')
$redis_master_host = hiera('CONFIG_REDIS_MASTER_HOST')

class { '::redis':
  bind       => $redis_master_host,
  port       => $redis_port,
  appendonly => true,
  daemonize  => false,
}
