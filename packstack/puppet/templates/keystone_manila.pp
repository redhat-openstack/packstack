
class { 'manila::keystone::auth':
  password         => hiera('CONFIG_MANILA_KS_PW'),
  public_address   => hiera('CONFIG_CONTROLLER_HOST'),
  admin_address    => hiera('CONFIG_CONTROLLER_HOST'),
  internal_address => hiera('CONFIG_CONTROLLER_HOST'),
}
