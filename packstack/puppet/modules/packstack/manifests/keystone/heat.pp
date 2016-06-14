class packstack::keystone::heat ()
{
    $heat_protocol = 'http'
    $heat_port = '8004'
    $heat_api_host = hiera('CONFIG_KEYSTONE_HOST_URL')
    $heat_url = "${heat_protocol}://${heat_api_host}:${heat_port}/v1/%(tenant_id)s"

    # heat::keystone::auth
    class { '::heat::keystone::auth':
      region                    => hiera('CONFIG_KEYSTONE_REGION'),
      password                  => hiera('CONFIG_HEAT_KS_PW'),
      public_url                => $heat_url,
      admin_url                 => $heat_url,
      internal_url              => $heat_url,
      configure_delegated_roles => true,
    }
}
