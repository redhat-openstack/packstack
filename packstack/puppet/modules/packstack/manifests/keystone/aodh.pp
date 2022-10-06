class packstack::keystone::aodh ()
{
    $keystone_host_url = lookup('CONFIG_KEYSTONE_HOST_URL')

    class { 'aodh::keystone::auth':
      region       => lookup('CONFIG_KEYSTONE_REGION'),
      password     => lookup('CONFIG_AODH_KS_PW'),
      public_url   => "http://${keystone_host_url}:8042",
      admin_url    => "http://${keystone_host_url}:8042",
      internal_url => "http://${keystone_host_url}:8042",
    }
}
