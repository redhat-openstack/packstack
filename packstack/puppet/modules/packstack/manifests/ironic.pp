class packstack::ironic ()
{
    create_resources(packstack::firewall, lookup('FIREWALL_IRONIC_API_RULES', undef, undef, {}))

    class { 'ironic::api::authtoken':
      auth_url             => lookup('CONFIG_KEYSTONE_ADMIN_URL'),
      www_authenticate_uri => lookup('CONFIG_KEYSTONE_PUBLIC_URL_VERSIONLESS'),
      password             => lookup('CONFIG_IRONIC_KS_PW'),
    }

    class { 'ironic::api': }

    class { 'ironic::client': }

    class { 'ironic::conductor': }
}
