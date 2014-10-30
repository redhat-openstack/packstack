
class { 'heat::api_cfn': }

$heat_cfn_cfg_ctrl_host = hiera('CONFIG_CONTROLLER_HOST')

class { 'heat::keystone::auth_cfn':
  admin_address    => $heat_cfn_cfg_ctrl_host,
  public_address   => $heat_cfn_cfg_ctrl_host,
  internal_address => $heat_cfn_cfg_ctrl_host,
  password         => hiera('CONFIG_HEAT_KS_PW'),
}

