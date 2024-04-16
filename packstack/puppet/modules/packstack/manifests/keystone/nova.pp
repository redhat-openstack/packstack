class packstack::keystone::nova ()
{
    $nova_protocol = 'http'
    $nova_host = lookup('CONFIG_KEYSTONE_HOST_URL')
    $nova_port = '8774'
    $nova_url = "${nova_protocol}://${nova_host}:${nova_port}/v2.1"


    class { 'nova::keystone::auth':
      roles        => ['admin', 'service'],
      region       => lookup('CONFIG_KEYSTONE_REGION'),
      password     => lookup('CONFIG_NOVA_KS_PW'),
      public_url   => $nova_url,
      admin_url    => $nova_url,
      internal_url => $nova_url,
    }
}
