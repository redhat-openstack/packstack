class packstack::keystone::trove ()
{
    $trove_protocol = 'http'
    $trove_host = hiera('CONFIG_KEYSTONE_HOST_URL')
    $trove_port = '8779'
    $trove_url = "${trove_protocol}://${trove_host}:$trove_port/v1.0/%(tenant_id)s"

    class { '::trove::keystone::auth':
      region       => hiera('CONFIG_KEYSTONE_REGION'),
      password     => hiera('CONFIG_TROVE_KS_PW'),
      public_url   => $trove_url,
      admin_url    => $trove_url,
      internal_url => $trove_url,
    }
}
