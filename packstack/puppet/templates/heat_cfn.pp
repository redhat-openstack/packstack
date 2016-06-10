
class { '::heat::api_cfn':
  workers => $service_workers
}

$heat_cfn_cfg_ctrl_host = hiera('CONFIG_KEYSTONE_HOST_URL')

class { '::heat::keystone::auth_cfn':
  admin_url    => "http://$heat_cfn_cfg_ctrl_host:8000/v1",
  public_url   => "http://$heat_cfn_cfg_ctrl_host:8000/v1",
  internal_url => "http://$heat_cfn_cfg_ctrl_host:8000/v1",
  password     => hiera('CONFIG_HEAT_KS_PW'),
}
