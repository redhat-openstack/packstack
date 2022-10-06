class packstack::memcached ()
{
    $memcached_bind_host = lookup('CONFIG_IP_VERSION') ? {
      'ipv6'  => '::',
      default => '0.0.0.0',
      # TO-DO(mmagr): Add IPv6 support when hostnames are used
    }

    class { 'memcached':
      listen_ip  => $memcached_bind_host,
      max_memory => '10%',
    }
}
