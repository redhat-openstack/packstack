# heat::keystone::auth
class { '::heat::keystone::auth':
  region                    => hiera('CONFIG_KEYSTONE_REGION'),
  password                  => hiera('CONFIG_HEAT_KS_PW'),
  public_address            => hiera('CONFIG_KEYSTONE_HOST_URL'),
  admin_address             => hiera('CONFIG_KEYSTONE_HOST_URL'),
  internal_address          => hiera('CONFIG_KEYSTONE_HOST_URL'),
  configure_delegated_roles => true,
}

$is_heat_cfn_install = hiera('CONFIG_HEAT_CFN_INSTALL')

if $is_heat_cfn_install == 'y' {
  # heat::keystone::cfn
  class { '::heat::keystone::auth_cfn':
    password         => hiera('CONFIG_HEAT_KS_PW'),
    public_address   => hiera('CONFIG_KEYSTONE_HOST_URL'),
    admin_address    => hiera('CONFIG_KEYSTONE_HOST_URL'),
    internal_address => hiera('CONFIG_KEYSTONE_HOST_URL'),
  }
}
