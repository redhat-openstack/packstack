class packstack::trove ()
{
    create_resources(packstack::firewall, lookup('FIREWALL_TROVE_API_RULES', undef, undef, {}))

    $bind_host = lookup('CONFIG_IP_VERSION') ? {
      'ipv6'  => '::0',
      default => '0.0.0.0',
      # TO-DO(mmagr): Add IPv6 support when hostnames are used
    }

    class { 'trove::keystone::authtoken':
      password             => lookup('CONFIG_TROVE_KS_PW'),
      www_authenticate_uri => lookup('CONFIG_KEYSTONE_PUBLIC_URL_VERSIONLESS'),
      auth_url             => lookup('CONFIG_KEYSTONE_ADMIN_URL'),
    }

    class { 'trove::logging':
      debug => lookup('CONFIG_DEBUG_MODE'),
    }

    class { 'trove::service_credentials':
      password => lookup('CONFIG_TROVE_KS_PW'),
      auth_url => lookup('CONFIG_KEYSTONE_PUBLIC_URL_VERSIONLESS'),
    }

    class { 'trove::api':
      bind_host => $bind_host,
      enabled   => true,
      cert_file => false,
      key_file  => false,
      ca_file   => false,
      workers   => lookup('CONFIG_SERVICE_WORKERS'),
    }

    class { 'trove::conductor':
      workers => lookup('CONFIG_SERVICE_WORKERS'),
    }

    class { 'trove::guestagent::service_credentials':
      password => lookup('CONFIG_TROVE_KS_PW'),
      auth_url => lookup('CONFIG_KEYSTONE_PUBLIC_URL_VERSIONLESS'),
    }
    class { 'trove::taskmanager': }
}
