class packstack::neutron::notifications ()
{
    $neutron_notif_cfg_ctrl_host = hiera('CONFIG_KEYSTONE_HOST_URL')

    # Configure nova notifications system
    class { '::neutron::server::notifications':
      username    => 'nova',
      password    => hiera('CONFIG_NOVA_KS_PW'),
      tenant_name => 'services',
      auth_url    => hiera('CONFIG_KEYSTONE_ADMIN_URL'),
      region_name => hiera('CONFIG_KEYSTONE_REGION'),
    }
}
