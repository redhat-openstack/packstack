class packstack::keystone::magnum ()
{
    $magnum_protocol = 'http'
    $magnum_host = hiera('CONFIG_KEYSTONE_HOST_URL')
    $magnum_port = '9511'
    $magnum_url = "${magnum_protocol}://${magnum_host}:$magnum_port/v1"

    class { '::magnum::keystone::auth':
      region          => hiera('CONFIG_KEYSTONE_REGION'),
      password        => hiera('CONFIG_MAGNUM_KS_PW'),
      public_url      => $magnum_url,
      admin_url       => $magnum_url,
      internal_url    => $magnum_url
    }

    class { '::magnum::keystone::domain':
      domain_password => hiera('CONFIG_MAGNUM_KS_PW'),
    }
}
