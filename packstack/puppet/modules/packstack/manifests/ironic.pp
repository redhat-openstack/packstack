class packstack::ironic ()
{
    create_resources(packstack::firewall, lookup('FIREWALL_IRONIC_API_RULES', undef, undef, {}))

    ironic_config {
      'glance/glance_host': value => lookup('CONFIG_STORAGE_HOST_URL');
    }

    class { 'ironic::api::authtoken':
      www_authenticate_uri => lookup('CONFIG_KEYSTONE_PUBLIC_URL'),
      password             => lookup('CONFIG_IRONIC_KS_PW'),
    }

    class { 'ironic::api': }

    class { 'ironic::client': }

    class { 'ironic::conductor': }
}
