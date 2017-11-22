class packstack::trove ()
{
    create_resources(packstack::firewall, hiera('FIREWALL_TROVE_API_RULES', {}))

    $bind_host = hiera('CONFIG_IP_VERSION') ? {
      'ipv6'  => '::0',
      default => '0.0.0.0',
      # TO-DO(mmagr): Add IPv6 support when hostnames are used
    }

    class { '::trove::keystone::authtoken':
      password => hiera('CONFIG_TROVE_KS_PW'),
      auth_url => hiera('CONFIG_KEYSTONE_PUBLIC_URL_VERSIONLESS'),
    }

    class { '::trove::api':
      bind_host         => $bind_host,
      enabled           => true,
      cert_file         => false,
      key_file          => false,
      ca_file           => false,
      debug             => hiera('CONFIG_DEBUG_MODE'),
      workers           => hiera('CONFIG_SERVICE_WORKERS'),
    }

    class { '::trove::conductor':
      auth_url => hiera('CONFIG_KEYSTONE_PUBLIC_URL_VERSIONLESS'),
      debug    => hiera('CONFIG_DEBUG_MODE'),
      workers  => hiera('CONFIG_SERVICE_WORKERS'),
    }

    class { '::trove::taskmanager':
      auth_url => hiera('CONFIG_KEYSTONE_PUBLIC_URL_VERSIONLESS'),
      debug    => hiera('CONFIG_DEBUG_MODE'),
    }
}
