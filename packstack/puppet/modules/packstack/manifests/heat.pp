class packstack::heat ()
{
    create_resources(packstack::firewall, hiera('FIREWALL_HEAT_RULES', {}))

    class { '::heat::api':
      workers => hiera('CONFIG_SERVICE_WORKERS'),
    }

    $keystone_admin = hiera('CONFIG_KEYSTONE_ADMIN_USERNAME')
    $heat_cfg_ctrl_host = hiera('CONFIG_KEYSTONE_HOST_URL')

    class { '::heat::engine':
      heat_metadata_server_url      => "http://${heat_cfg_ctrl_host}:8000",
      heat_waitcondition_server_url => "http://${heat_cfg_ctrl_host}:8000/v1/waitcondition",
      heat_watch_server_url         => "http://${heat_cfg_ctrl_host}:8003",
      auth_encryption_key           => hiera('CONFIG_HEAT_AUTH_ENC_KEY'),
      num_engine_workers            => hiera('CONFIG_SERVICE_WORKERS'),
    }

    class { '::heat::keystone::domain':
      domain_name       => hiera('CONFIG_HEAT_DOMAIN'),
      domain_admin      => hiera('CONFIG_HEAT_DOMAIN_ADMIN'),
      domain_password   => hiera('CONFIG_HEAT_DOMAIN_PASSWORD'),
    }
}
