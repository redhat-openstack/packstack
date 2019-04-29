class packstack::keystone::placement ()
{
    $placement_protocol = 'http'
    $placement_host = hiera('CONFIG_KEYSTONE_HOST_URL')
    $placement_port = '8778'
    $placement_url = "${placement_protocol}://${placement_host}:${placement_port}/placement"

    class { '::placement::keystone::authtoken':
      password             => hiera('CONFIG_NOVA_KS_PW'),
      user_domain_name     => 'Default',
      project_domain_name  => 'Default',
      auth_url             => hiera('CONFIG_KEYSTONE_ADMIN_URL'),
      www_authenticate_uri => hiera('CONFIG_KEYSTONE_PUBLIC_URL_VERSIONLESS'),
    }

    class { '::placement::keystone::auth':
      public_url   => $placement_url,
      internal_url => $placement_url,
      admin_url    => $placement_url,
      password     => hiera('CONFIG_NOVA_KS_PW'),
    }
}
