class packstack::keystone::ceilometer ()
{
    $ceilometer_protocol = 'http'
    $ceilometer_port = '8777'
    $ceilometer_api_host = hiera('CONFIG_KEYSTONE_HOST_URL')
    $ceilometer_url = "${ceilometer_protocol}://${ceilometer_api_host}:${ceilometer_port}"

    class { '::ceilometer::keystone::auth':
      region       => hiera('CONFIG_KEYSTONE_REGION'),
      password     => hiera('CONFIG_CEILOMETER_KS_PW'),
      public_url   => $ceilometer_url,
      admin_url    => $ceilometer_url,
      internal_url => $ceilometer_url,
    }
}
