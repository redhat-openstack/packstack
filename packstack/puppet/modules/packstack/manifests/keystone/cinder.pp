class packstack::keystone::cinder ()
{
    $cinder_protocol = 'http'
    $cinder_host = hiera('CONFIG_STORAGE_HOST_URL')
    $cinder_port = '8776'
    $cinder_url = "${cinder_protocol}://${cinder_host}:${cinder_port}"

    class { 'cinder::keystone::auth':
      region          => hiera('CONFIG_KEYSTONE_REGION'),
      password        => hiera('CONFIG_CINDER_KS_PW'),
      public_url_v3   => "${cinder_url}/v3",
      internal_url_v3 => "${cinder_url}/v3",
      admin_url_v3    => "${cinder_url}/v3",
    }
}
