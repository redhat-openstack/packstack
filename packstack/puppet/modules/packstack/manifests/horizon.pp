class packstack::horizon ()
{
    $is_django_debug = hiera('CONFIG_DEBUG_MODE') ? {
      true  => 'True',
      false => 'False',
    }

    $bind_host = hiera('CONFIG_IP_VERSION') ? {
      'ipv6'  => '::0',
      default => '0.0.0.0',
      # TO-DO(mmagr): Add IPv6 support when hostnames are used
    }

    $horizon_ssl = hiera('CONFIG_HORIZON_SSL') ? {
      'y' => true,
      'n' => false,
    }

    class {'::horizon':
      secret_key            => hiera('CONFIG_HORIZON_SECRET_KEY'),
      keystone_url          => hiera('CONFIG_KEYSTONE_PUBLIC_URL'),
      keystone_default_role => '_member_',
      server_aliases        => [hiera('CONFIG_CONTROLLER_HOST'), $::fqdn, 'localhost'],
      allowed_hosts         => '*',
      hypervisor_options    => {'can_set_mount_point' => false, },
      django_debug          => $is_django_debug,
      django_session_engine => 'django.contrib.sessions.backends.cache',
      cache_backend         => 'django.core.cache.backends.memcached.MemcachedCache',
      cache_server_ip       => '127.0.0.1',
      cache_server_port     => '11211',
      file_upload_temp_dir  => '/var/tmp',
      listen_ssl            => $horizon_ssl,
      horizon_cert          => hiera('CONFIG_HORIZON_SSL_CERT', undef),
      horizon_key           => hiera('CONFIG_HORIZON_SSL_KEY', undef),
      horizon_ca            => hiera('CONFIG_HORIZON_SSL_CACERT', undef),
      neutron_options       => {
        'enable_firewall' => hiera('CONFIG_HORIZON_NEUTRON_FW'),
        'enable_vpn'      => hiera('CONFIG_HORIZON_NEUTRON_VPN'),
        'enable_lb'       => hiera('CONFIG_HORIZON_NEUTRON_LB'),
      },
    }

    if hiera('CONFIG_LBAAS_INSTALL') == 'y' {
      ensure_packages(['openstack-neutron-lbaas-ui'], {'ensure' => 'present'})
    }

    if hiera('CONFIG_MAGNUM_INSTALL') == 'y' {
      ensure_packages(['openstack-magnum-ui'], {'ensure' => 'present'})
    }

   if hiera('CONFIG_IRONIC_INSTALL') == 'y' {
      ensure_packages(['openstack-ironic-ui'], {'ensure' => 'present'})
    }

   if hiera('CONFIG_TROVE_INSTALL') == 'y' {
      ensure_packages(['openstack-trove-ui'], {'ensure' => 'present'})
    }

   if hiera('CONFIG_SAHARA_INSTALL') == 'y' {
      ensure_packages(['openstack-sahara-ui'], {'ensure' => 'present'})
    }

    include '::packstack::memcached'

    $firewall_port = hiera('CONFIG_HORIZON_PORT')

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
