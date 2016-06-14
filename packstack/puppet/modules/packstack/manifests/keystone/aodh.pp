class packstack::keystone::aodh ()
{
    $keystone_host_url = hiera('CONFIG_KEYSTONE_HOST_URL')

    class { '::aodh::keystone::auth':
      region       => hiera('CONFIG_KEYSTONE_REGION'),
      password     => hiera('CONFIG_AODH_KS_PW'),
      public_url   => "http://${keystone_host_url}:8042",
      admin_url    => "http://${keystone_host_url}:8042",
      internal_url => "http://${keystone_host_url}:8042",
    }
}
