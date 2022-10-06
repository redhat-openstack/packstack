class packstack::keystone::neutron ()
{
    $neutron_protocol = 'http'
    $neutron_host = lookup('CONFIG_KEYSTONE_HOST_URL')
    $neutron_port = '9696'
    $neutron_url = "${neutron_protocol}://${neutron_host}:${neutron_port}"

    class { 'neutron::keystone::auth':
      region       => lookup('CONFIG_KEYSTONE_REGION'),
      password     => lookup('CONFIG_NEUTRON_KS_PW'),
      public_url   => $neutron_url,
      admin_url    => $neutron_url,
      internal_url => $neutron_url,
    }
}
