class packstack::keystone::ceilometer ()
{
    class { 'ceilometer::keystone::auth':
      region       => hiera('CONFIG_KEYSTONE_REGION'),
      password     => hiera('CONFIG_CEILOMETER_KS_PW'),
    }
}
