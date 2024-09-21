class packstack::keystone::cinder ()
{
    $cinder_protocol = 'http'
    $cinder_host = lookup('CONFIG_STORAGE_HOST_URL')
    $cinder_port = '8776'
    $cinder_url = "${cinder_protocol}://${cinder_host}:${cinder_port}"

    class { 'cinder::keystone::auth':
      region          => lookup('CONFIG_KEYSTONE_REGION'),
      password        => lookup('CONFIG_CINDER_KS_PW'),
      roles           => ['admin', 'service'],
      public_url_v3   => "${cinder_url}/v3",
      internal_url_v3 => "${cinder_url}/v3",
      admin_url_v3    => "${cinder_url}/v3",
    }
}
