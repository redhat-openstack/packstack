class packstack::keystone::gnocchi ()
{
    $gnocchi_keystone_host_url = lookup('CONFIG_KEYSTONE_HOST_URL')

    class { 'gnocchi::keystone::auth':
      region       => lookup('CONFIG_KEYSTONE_REGION'),
      password     => lookup('CONFIG_GNOCCHI_KS_PW'),
      public_url   => "http://${gnocchi_keystone_host_url}:8041",
      admin_url    => "http://${gnocchi_keystone_host_url}:8041",
      internal_url => "http://${gnocchi_keystone_host_url}:8041",
    }
}
