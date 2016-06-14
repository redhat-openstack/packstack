class packstack::memcached ()
{
    # hack for memcached, for now we bind to localhost on ipv6
    # https://bugzilla.redhat.com/show_bug.cgi?id=1210658
    $memcached_bind_host = hiera('CONFIG_IP_VERSION') ? {
      'ipv6'  => 'localhost6',
      default => '0.0.0.0',
      # TO-DO(mmagr): Add IPv6 support when hostnames are used
    }

    class { '::memcached':
      listen_ip  => $memcached_bind_host,
      max_memory => '10%',
    }
}
