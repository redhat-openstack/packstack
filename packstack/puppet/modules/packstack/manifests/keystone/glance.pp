class packstack::keystone::glance ()
{
    $glance_protocol = 'http'
    $glance_port = '9292'
    $glance_api_host = lookup('CONFIG_STORAGE_HOST_URL')
    $glance_url = "${glance_protocol}://${glance_api_host}:${glance_port}"

    class { 'glance::keystone::auth':
      region       => lookup('CONFIG_KEYSTONE_REGION'),
      password     => lookup('CONFIG_GLANCE_KS_PW'),
      public_url   => $glance_url,
      admin_url    => $glance_url,
      internal_url => $glance_url,
    }
}
