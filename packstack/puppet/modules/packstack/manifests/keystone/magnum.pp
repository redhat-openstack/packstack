class packstack::keystone::magnum ()
{
    $magnum_protocol = 'http'
    $magnum_host = lookup('CONFIG_KEYSTONE_HOST_URL')
    $magnum_port = '9511'
    $magnum_url = "${magnum_protocol}://${magnum_host}:${magnum_port}/v1"

    class { 'magnum::keystone::auth':
      region       => lookup('CONFIG_KEYSTONE_REGION'),
      password     => lookup('CONFIG_MAGNUM_KS_PW'),
      public_url   => $magnum_url,
      admin_url    => $magnum_url,
      internal_url => $magnum_url
    }

    class { 'magnum::keystone::domain':
      domain_password => lookup('CONFIG_MAGNUM_KS_PW'),
    }
}
