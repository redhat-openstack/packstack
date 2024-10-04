class packstack::keystone::placement ()
{
    $placement_protocol = 'http'
    $placement_host = lookup('CONFIG_KEYSTONE_HOST_URL')
    $placement_port = '8778'
    $placement_url = "${placement_protocol}://${placement_host}:${placement_port}"

    class { 'placement::keystone::authtoken':
      password             => lookup('CONFIG_NOVA_KS_PW'),
      auth_url             => lookup('CONFIG_KEYSTONE_ADMIN_URL'),
      www_authenticate_uri => lookup('CONFIG_KEYSTONE_PUBLIC_URL_VERSIONLESS'),
    }

    class { 'placement::keystone::auth':
      public_url   => $placement_url,
      internal_url => $placement_url,
      admin_url    => $placement_url,
      password     => lookup('CONFIG_NOVA_KS_PW'),
    }
}
