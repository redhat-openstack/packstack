class packstack::heat::cfn ()
{
    create_resources(packstack::firewall, hiera('FIREWALL_HEAT_CFN_RULES', {}))

    class { '::heat::api_cfn':
      workers => hiera('CONFIG_SERVICE_WORKERS'),
    }

    $heat_cfn_cfg_ctrl_host = hiera('CONFIG_KEYSTONE_HOST_URL')

    class { '::heat::keystone::auth_cfn':
      admin_url    => "http://$heat_cfn_cfg_ctrl_host:8000/v1",
      public_url   => "http://$heat_cfn_cfg_ctrl_host:8000/v1",
      internal_url => "http://$heat_cfn_cfg_ctrl_host:8000/v1",
      password     => hiera('CONFIG_HEAT_KS_PW'),
    }
}
