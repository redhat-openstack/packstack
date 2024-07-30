class packstack::redis ()
{
    create_resources(packstack::firewall, lookup('FIREWALL_REDIS_RULES', undef, undef, {}))

    $redis_port = Integer(lookup('CONFIG_REDIS_PORT'))
    $redis_host = lookup('CONFIG_REDIS_HOST')

    class { 'redis':
      bind           => $redis_host,
      port           => $redis_port,
      appendonly     => true,
      daemonize      => false,
      unixsocket     => '',
    }
}
