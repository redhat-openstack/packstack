class packstack::heat::cfn ()
{
    create_resources(packstack::firewall, lookup('FIREWALL_HEAT_CFN_RULES', undef, undef, {}))

    class { 'heat::api_cfn':
      workers => lookup('CONFIG_SERVICE_WORKERS'),
    }

    $heat_cfn_cfg_ctrl_host = lookup('CONFIG_KEYSTONE_HOST_URL')

    class { 'heat::keystone::auth_cfn':
      admin_url    => "http://${heat_cfn_cfg_ctrl_host}:8000/v1",
      public_url   => "http://${heat_cfn_cfg_ctrl_host}:8000/v1",
      internal_url => "http://${heat_cfn_cfg_ctrl_host}:8000/v1",
      password     => lookup('CONFIG_HEAT_KS_PW'),
    }
}
