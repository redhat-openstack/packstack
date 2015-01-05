$redis_master_host = hiera('CONFIG_REDIS_MASTER_HOST')
$redis_master_port = hiera('CONFIG_REDIS_PORT')
$redis_master_name = hiera('CONFIG_REDIS_MASTER_NAME')
$redis_sentinel_quorum = hiera('CONFIG_REDIS_SENTINEL_QUORUM')

class { 'redis::sentinel':
  master_name => "${redis_master_name}",
  redis_host  => $redis_master_host,
  redis_port  => $redis_master_port,
  quorum      => $redis_sentinel_quorum,
}
