class packstack::redis ()
{
    create_resources(packstack::firewall, hiera('FIREWALL_REDIS_RULES', {}))

    $redis_port = hiera('CONFIG_REDIS_PORT')
    $redis_host = hiera('CONFIG_REDIS_HOST')

    class { '::redis':
      bind       => $redis_host,
      port       => $redis_port,
      appendonly => true,
      daemonize  => false,
      unixsocket => false,
    }
}
