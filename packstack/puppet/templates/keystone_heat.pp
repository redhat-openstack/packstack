# heat::keystone::auth
class { 'heat::keystone::auth':
  region           => hiera('CONFIG_KEYSTONE_REGION'),
  password         => hiera('CONFIG_HEAT_KS_PW'),
  public_address   => hiera('CONFIG_CONTROLLER_HOST'),
  admin_address    => hiera('CONFIG_CONTROLLER_HOST'),
  internal_address => hiera('CONFIG_CONTROLLER_HOST'),
}

$is_heat_cfn_install = hiera('CONFIG_HEAT_CFN_INSTALL')

if $is_heat_cfn_install == 'y' {
  # heat::keystone::cfn
  class { "heat::keystone::auth_cfn":
    password         => hiera('CONFIG_HEAT_KS_PW'),
    public_address   => hiera('CONFIG_CONTROLLER_HOST'),
    admin_address    => hiera('CONFIG_CONTROLLER_HOST'),
    internal_address => hiera('CONFIG_CONTROLLER_HOST'),
  }
}
