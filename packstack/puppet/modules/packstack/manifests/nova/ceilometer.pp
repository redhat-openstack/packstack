class packstack::nova::ceilometer ()
{
    class { 'ceilometer::agent::service_credentials':
      auth_url     => lookup('CONFIG_KEYSTONE_PUBLIC_URL_VERSIONLESS'),
      password     => lookup('CONFIG_CEILOMETER_KS_PW'),
      region_name  => lookup('CONFIG_KEYSTONE_REGION'),
    }

    ensure_packages(['openstack-ceilometer-ipmi'], {'ensure' => 'present'})

    class { 'ceilometer::agent::polling': }

    Package['openstack-ceilometer-ipmi'] -> Service['ceilometer-polling']
}
