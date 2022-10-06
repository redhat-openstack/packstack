class packstack::heat ()
{
    create_resources(packstack::firewall, lookup('FIREWALL_HEAT_RULES', undef, undef, {}))

    class { 'heat::api':
      workers => lookup('CONFIG_SERVICE_WORKERS'),
    }

    $keystone_admin = lookup('CONFIG_KEYSTONE_ADMIN_USERNAME')
    $heat_cfg_ctrl_host = lookup('CONFIG_KEYSTONE_HOST_URL')

    class { 'heat::engine':
      heat_metadata_server_url      => "http://${heat_cfg_ctrl_host}:8000",
      heat_waitcondition_server_url => "http://${heat_cfg_ctrl_host}:8000/v1/waitcondition",
      auth_encryption_key           => lookup('CONFIG_HEAT_AUTH_ENC_KEY'),
      num_engine_workers            => lookup('CONFIG_SERVICE_WORKERS'),
    }

    class { 'heat::keystone::domain':
      domain_name     => lookup('CONFIG_HEAT_DOMAIN'),
      domain_admin    => lookup('CONFIG_HEAT_DOMAIN_ADMIN'),
      domain_password => lookup('CONFIG_HEAT_DOMAIN_PASSWORD'),
    }
}
