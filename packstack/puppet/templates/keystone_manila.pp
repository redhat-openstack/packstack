
class { '::manila::keystone::auth':
  password         => hiera('CONFIG_MANILA_KS_PW'),
  public_address   => hiera('CONFIG_KEYSTONE_HOST_URL'),
  admin_address    => hiera('CONFIG_KEYSTONE_HOST_URL'),
  internal_address => hiera('CONFIG_KEYSTONE_HOST_URL'),
}
