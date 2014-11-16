$redis_host = hiera('CONFIG_REDIS_HOST')
$redis_port = hiera('CONFIG_REDIS_PORT')

class { 'redis':
  bind       => $redis_host,
  port       => $redis_port,
  appendonly => true,
  daemonize  => false,
}
