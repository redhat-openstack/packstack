$redis_host = hiera('CONFIG_REDIS_HOST')
$redis_port = hiera('CONFIG_REDIS_PORT')
$redis_master_host = hiera('CONFIG_REDIS_MASTER_HOST')

class { '::redis':
  bind       => '0.0.0.0',
  port       => $redis_port,
  appendonly => true,
  daemonize  => false,
  slaveof    => "${redis_master_host} ${redis_port}",
}
