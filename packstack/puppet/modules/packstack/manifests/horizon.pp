class packstack::horizon ()
{
    $log_level = lookup('CONFIG_DEBUG_MODE') ? {
      true    => 'DEBUG',
      default => 'INFO',
    }

    $bind_host = lookup('CONFIG_IP_VERSION') ? {
      'ipv6'  => '::0',
      default => '0.0.0.0',
      # TO-DO(mmagr): Add IPv6 support when hostnames are used
    }

    $horizon_ssl = lookup('CONFIG_HORIZON_SSL') ? {
      'y'     => true,
      default => false,
    }

    class { 'horizon':
      secret_key            => lookup('CONFIG_HORIZON_SECRET_KEY'),
      keystone_url          => lookup('CONFIG_KEYSTONE_PUBLIC_URL'),
      server_aliases        => [lookup('CONFIG_CONTROLLER_HOST'), $facts['networking']['fqdn'], 'localhost'],
      allowed_hosts         => '*',
      django_session_engine => 'django.contrib.sessions.backends.cache',
      cache_backend         => 'django.core.cache.backends.memcached.PyMemcacheCache',
      cache_server_ip       => '127.0.0.1',
      cache_server_port     => '11211',
      file_upload_temp_dir  => '/var/tmp',
      listen_ssl            => $horizon_ssl,
      ssl_cert              => lookup('CONFIG_HORIZON_SSL_CERT', undef, undef, undef),
      ssl_key               => lookup('CONFIG_HORIZON_SSL_KEY', undef, undef, undef),
      ssl_ca                => lookup('CONFIG_HORIZON_SSL_CACERT', undef, undef, undef),
      ssl_verify_client     => 'optional',
      log_level             => $log_level,
      django_log_level      => 'INFO',
      neutron_options       => {
        'enable_vpn' => lookup('CONFIG_HORIZON_NEUTRON_VPN'),
      },
    }

    if lookup('CONFIG_MAGNUM_INSTALL') == 'y' {
      horizon::dashboard { 'magnum': }
    }

    if lookup('CONFIG_IRONIC_INSTALL') == 'y' {
      include horizon::dashboards::ironic
    }

    if lookup('CONFIG_TROVE_INSTALL') == 'y' {
      horizon::dashboard { 'trove': }
    }

    if lookup('CONFIG_HEAT_INSTALL') == 'y' {
      include horizon::dashboards::heat
    }

    if lookup('CONFIG_MANILA_INSTALL') == 'y' {
      include horizon::dashboards::manila
    }

    include packstack::memcached

    $firewall_port = lookup('CONFIG_HORIZON_PORT')

    firewall { "001 horizon ${firewall_port} incoming":
      proto  => 'tcp',
      dport  => [$firewall_port],
      jump   => 'accept',
    }

    if str2bool($facts['os']['selinux']['enabled']) {
      selboolean{ 'httpd_can_network_connect':
        value      => on,
        persistent => true,
      }
    }
}
