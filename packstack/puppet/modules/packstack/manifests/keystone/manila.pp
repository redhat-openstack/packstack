class packstack::keystone::manila ()
{
    $manila_protocol = 'http'
    $manila_host = lookup('CONFIG_STORAGE_HOST_URL')
    $manila_port = '8786'
    $manila_url = "${manila_protocol}://${manila_host}:${manila_port}/v1/%(tenant_id)s"
    $manila_url_v2 = "${manila_protocol}://${manila_host}:${manila_port}/v2/"

    class { 'manila::keystone::auth':
      password        => lookup('CONFIG_MANILA_KS_PW'),
      public_url      => $manila_url,
      admin_url       => $manila_url,
      internal_url    => $manila_url,
      public_url_v2   => $manila_url_v2,
      admin_url_v2    => $manila_url_v2,
      internal_url_v2 => $manila_url_v2,
    }
}
