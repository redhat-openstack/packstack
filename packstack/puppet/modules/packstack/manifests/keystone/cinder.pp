class packstack::keystone::cinder ()
{
    $cinder_protocol = 'http'
    $cinder_host = hiera('CONFIG_STORAGE_HOST_URL')
    $cinder_port = '8776'
    $cinder_url = "${cinder_protocol}://${cinder_host}:$cinder_port"

    class { '::cinder::keystone::auth':
      region          => hiera('CONFIG_KEYSTONE_REGION'),
      password        => hiera('CONFIG_CINDER_KS_PW'),
      public_url      => "${cinder_url}/v1/%(tenant_id)s",
      internal_url    => "${cinder_url}/v1/%(tenant_id)s",
      admin_url       => "${cinder_url}/v1/%(tenant_id)s",
      public_url_v2   => "${cinder_url}/v2/%(tenant_id)s",
      internal_url_v2 => "${cinder_url}/v2/%(tenant_id)s",
      admin_url_v2    => "${cinder_url}/v2/%(tenant_id)s",
      public_url_v3   => "${cinder_url}/v3/%(tenant_id)s",
      internal_url_v3 => "${cinder_url}/v3/%(tenant_id)s",
      admin_url_v3    => "${cinder_url}/v3/%(tenant_id)s",
    }
}
