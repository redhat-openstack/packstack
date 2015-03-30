
class { '::nova::keystone::auth':
  region           => hiera('CONFIG_KEYSTONE_REGION'),
  password         => hiera('CONFIG_NOVA_KS_PW'),
  public_address   => hiera('CONFIG_KEYSTONE_HOST_URL'),
  admin_address    => hiera('CONFIG_KEYSTONE_HOST_URL'),
  internal_address => hiera('CONFIG_KEYSTONE_HOST_URL'),
}
