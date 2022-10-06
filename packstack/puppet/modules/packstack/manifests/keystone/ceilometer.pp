class packstack::keystone::ceilometer ()
{
    class { 'ceilometer::keystone::auth':
      region       => lookup('CONFIG_KEYSTONE_REGION'),
      password     => lookup('CONFIG_CEILOMETER_KS_PW'),
    }
}
