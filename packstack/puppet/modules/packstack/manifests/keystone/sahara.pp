class packstack::keystone::sahara ()
{
    $sahara_protocol = 'http'
    $sahara_host = hiera('CONFIG_KEYSTONE_HOST_URL')
    $sahara_port = '8386'
    $sahara_url = "${sahara_protocol}://${sahara_host}:$sahara_port/v1.1/%(tenant_id)s"

    class { '::sahara::keystone::auth':
      password     => hiera('CONFIG_SAHARA_KS_PW'),
      public_url   => $sahara_url,
      admin_url    => $sahara_url,
      internal_url => $sahara_url,
    }
}
