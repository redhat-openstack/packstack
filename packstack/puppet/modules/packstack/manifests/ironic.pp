class packstack::ironic ()
{
    create_resources(packstack::firewall, hiera('FIREWALL_IRONIC_API_RULES', {}))

    ironic_config {
      'glance/glance_host': value => hiera('CONFIG_STORAGE_HOST_URL');
    }

    class { '::ironic::api':
      auth_uri       => hiera('CONFIG_KEYSTONE_PUBLIC_URL'),
      admin_password => hiera('CONFIG_IRONIC_KS_PW'),
    }

    class { '::ironic::client': }

    class { '::ironic::conductor': }
}
