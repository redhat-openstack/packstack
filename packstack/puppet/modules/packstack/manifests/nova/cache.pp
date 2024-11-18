class packstack::nova::cache ()
{
    $memcache_servers = lookup('CONFIG_IP_VERSION') ? {
      'ipv6'  => ['[::1]:11211'],
      default => ['127.0.0.1:11211'],
    }
    class { 'nova::cache':
      enabled          => true,
      backend          => 'dogpile.cache.pymemcache',
      memcache_servers => $memcache_servers,
    }
    include packstack::memcached
    Class['memcached'] -> Anchor['nova::service::begin']
}
