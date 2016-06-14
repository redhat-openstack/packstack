class packstack::nova::ceilometer ()
{
    class { '::ceilometer::agent::auth':
      auth_url      => hiera('CONFIG_KEYSTONE_PUBLIC_URL_VERSIONLESS'),
      auth_password => hiera('CONFIG_CEILOMETER_KS_PW'),
      auth_region   => hiera('CONFIG_KEYSTONE_REGION'),
    }

    class { '::ceilometer::agent::compute': }
}
