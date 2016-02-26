
class { '::heat::api_cfn':
  workers => $service_workers
}

$heat_cfn_cfg_ctrl_host = hiera('CONFIG_KEYSTONE_HOST_URL')

class { '::heat::keystone::auth_cfn':
  admin_address    => $heat_cfn_cfg_ctrl_host,
  public_address   => $heat_cfn_cfg_ctrl_host,
  internal_address => $heat_cfn_cfg_ctrl_host,
  password         => hiera('CONFIG_HEAT_KS_PW'),
}
