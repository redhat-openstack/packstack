class { 'sahara::keystone::auth':
  password         => hiera('CONFIG_SAHARA_KS_PW'),
  public_address   => hiera('CONFIG_SAHARA_HOST'),
  admin_address    => hiera('CONFIG_SAHARA_HOST'),
  internal_address => hiera('CONFIG_SAHARA_HOST'),
}
