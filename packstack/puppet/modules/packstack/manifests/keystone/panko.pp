class packstack::keystone::panko ()
{
    $keystone_host_url = hiera('CONFIG_KEYSTONE_HOST_URL')

    class { '::panko::keystone::auth':
      region       => hiera('CONFIG_KEYSTONE_REGION'),
      password     => hiera('CONFIG_PANKO_KS_PW'),
      public_url   => "http://${keystone_host_url}:8977",
      admin_url    => "http://${keystone_host_url}:8977",
      internal_url => "http://${keystone_host_url}:8977",
    }
}
