class packstack::horizon ()
{
    $is_django_debug = lookup('CONFIG_DEBUG_MODE') ? {
      true  => 'True',
      false => 'False',
    }

    $bind_host = lookup('CONFIG_IP_VERSION') ? {
      'ipv6'  => '::0',
      default => '0.0.0.0',
      # TO-DO(mmagr): Add IPv6 support when hostnames are used
    }

    $horizon_ssl = lookup('CONFIG_HORIZON_SSL') ? {
      'y' => true,
      'n' => false,
    }

    class { 'horizon':
      secret_key            => lookup('CONFIG_HORIZON_SECRET_KEY'),
      keystone_url          => lookup('CONFIG_KEYSTONE_PUBLIC_URL'),
      keystone_default_role => '_member_',
      server_aliases        => [lookup('CONFIG_CONTROLLER_HOST'), $::fqdn, 'localhost'],
      allowed_hosts         => '*',
      hypervisor_options    => {'can_set_mount_point' => false, },
      django_debug          => $is_django_debug,
      django_session_engine => 'django.contrib.sessions.backends.cache',
      cache_backend         => 'django.core.cache.backends.memcached.MemcachedCache',
      cache_server_ip       => '127.0.0.1',
      cache_server_port     => '11211',
      file_upload_temp_dir  => '/var/tmp',
      listen_ssl            => $horizon_ssl,
      ssl_cert              => lookup('CONFIG_HORIZON_SSL_CERT', undef, undef, undef),
      ssl_key               => lookup('CONFIG_HORIZON_SSL_KEY', undef, undef, undef),
      ssl_ca                => lookup('CONFIG_HORIZON_SSL_CACERT', undef, undef, undef),
      ssl_verify_client     => 'optional',
      neutron_options       => {
        'enable_vpn'      => lookup('CONFIG_HORIZON_NEUTRON_VPN'),
        'enable_lb'       => lookup('CONFIG_HORIZON_NEUTRON_LB'),
      },
    }

    if lookup('CONFIG_MAGNUM_INSTALL') == 'y' {
      ensure_packages(['openstack-magnum-ui'], {'ensure' => 'present'})
    }

    if lookup('CONFIG_IRONIC_INSTALL') == 'y' {
      ensure_packages(['openstack-ironic-ui'], {'ensure' => 'present'})
    }

    if lookup('CONFIG_TROVE_INSTALL') == 'y' {
      ensure_packages(['openstack-trove-ui'], {'ensure' => 'present'})
    }

    if lookup('CONFIG_SAHARA_INSTALL') == 'y' {
      ensure_packages(['openstack-sahara-ui'], {'ensure' => 'present'})
    }

    if lookup('CONFIG_HEAT_INSTALL') == 'y' {
      ensure_packages(['openstack-heat-ui'], {'ensure' => 'present'})
    }

    include packstack::memcached

    $firewall_port = lookup('CONFIG_HORIZON_PORT')

    firewall { "001 horizon ${firewall_port} incoming":
      proto  => 'tcp',
      dport  => [$firewall_port],
      action => 'accept',
    }

    if str2bool($::selinux) {
      selboolean{ 'httpd_can_network_connect':
        value      => on,
        persistent => true,
      }
    }
}
