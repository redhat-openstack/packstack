class packstack::nova::ceilometer ()
{
    class { '::ceilometer::agent::auth':
      auth_url      => hiera('CONFIG_KEYSTONE_PUBLIC_URL_VERSIONLESS'),
      auth_password => hiera('CONFIG_CEILOMETER_KS_PW'),
      auth_region   => hiera('CONFIG_KEYSTONE_REGION'),
    }

    ensure_packages(['openstack-ceilometer-ipmi'], {'ensure' => 'present'})

    class { '::ceilometer::agent::polling': }

    Package['openstack-ceilometer-ipmi'] -> Service['ceilometer-polling']
}
