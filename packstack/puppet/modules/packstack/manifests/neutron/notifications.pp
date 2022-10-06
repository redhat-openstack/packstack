class packstack::neutron::notifications ()
{
    $neutron_notif_cfg_ctrl_host = lookup('CONFIG_KEYSTONE_HOST_URL')

    # Configure nova notifications system
    class { 'neutron::server::notifications':
    }

    class { 'neutron::server::notifications::nova':
      username     => 'nova',
      password     => lookup('CONFIG_NOVA_KS_PW'),
      project_name => 'services',
      auth_url     => lookup('CONFIG_KEYSTONE_ADMIN_URL'),
      region_name  => lookup('CONFIG_KEYSTONE_REGION'),
    }
}
