class packstack::manila ()
{
    create_resources(packstack::firewall, lookup('FIREWALL_MANILA_API_RULES', undef, undef, {}))

    $bind_host = lookup('CONFIG_IP_VERSION') ? {
      'ipv6'  => '::0',
      default => '0.0.0.0',
      # TO-DO(mmagr): Add IPv6 support when hostnames are used
    }

    class { 'manila::keystone::authtoken':
      password             => lookup('CONFIG_MANILA_KS_PW'),
      www_authenticate_uri => lookup('CONFIG_KEYSTONE_PUBLIC_URL_VERSIONLESS'),
      auth_url             => lookup('CONFIG_KEYSTONE_ADMIN_URL'),
    }

    class { 'manila::api':
      bind_host          => $bind_host,
    }

    class { 'manila::scheduler':
    }

    class { 'manila::share':
    }

    class { 'manila::backends':
      enabled_share_backends => lookup('CONFIG_MANILA_BACKEND'),
    }
}
