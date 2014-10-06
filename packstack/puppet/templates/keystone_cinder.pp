
class { 'cinder::keystone::auth':
  region           => hiera('CONFIG_KEYSTONE_REGION'),
  password         => hiera('CONFIG_CINDER_KS_PW'),
  public_address   => hiera('CONFIG_STORAGE_HOST'),
  admin_address    => hiera('CONFIG_STORAGE_HOST'),
  internal_address => hiera('CONFIG_STORAGE_HOST'),
}

