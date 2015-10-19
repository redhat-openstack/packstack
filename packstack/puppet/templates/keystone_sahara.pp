class { '::sahara::keystone::auth':
  password     => hiera('CONFIG_SAHARA_KS_PW'),
  public_url   => hiera('CONFIG_SAHARA_URL'),
  admin_url    => hiera('CONFIG_SAHARA_URL'),
  internal_url => hiera('CONFIG_SAHARA_URL'),
}
