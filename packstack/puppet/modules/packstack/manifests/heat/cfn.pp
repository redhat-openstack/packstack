class packstack::heat::cfn ()
{
    create_resources(packstack::firewall, lookup('FIREWALL_HEAT_CFN_RULES', undef, undef, {}))

    $bind_host = lookup('CONFIG_IP_VERSION') ? {
      'ipv6'  => '::0',
      default => '0.0.0.0',
    }

    class { 'heat::api_cfn':
      service_name => 'httpd',
    }
    class { 'heat::wsgi::apache_api_cfn':
      bind_host => $bind_host,
      workers   => lookup('CONFIG_SERVICE_WORKERS'),
    }

    $heat_cfn_cfg_ctrl_host = lookup('CONFIG_KEYSTONE_HOST_URL')

    class { 'heat::keystone::auth_cfn':
      admin_url    => "http://${heat_cfn_cfg_ctrl_host}:8000/v1",
      public_url   => "http://${heat_cfn_cfg_ctrl_host}:8000/v1",
      internal_url => "http://${heat_cfn_cfg_ctrl_host}:8000/v1",
      password     => lookup('CONFIG_HEAT_KS_PW'),
    }
}
