class packstack::provision::bridge ()
{
    $provision_neutron_br    = str2bool(hiera('CONFIG_NEUTRON_INSTALL'))
    $setup_ovs_bridge        = str2bool(hiera('CONFIG_PROVISION_OVS_BRIDGE'))
    $public_bridge_name      = hiera('CONFIG_NEUTRON_L3_EXT_BRIDGE', 'br-ex')
    $provision_tempest_br    = str2bool(hiera('CONFIG_PROVISION_TEMPEST'))
    $provision_demo_br       = str2bool(hiera('CONFIG_PROVISION_DEMO'))

    $neutron_user_password   = hiera('CONFIG_NEUTRON_KS_PW')

    if $provision_demo_br {
      $floating_range_br = hiera('CONFIG_PROVISION_DEMO_FLOATRANGE')
    } elsif $provision_tempest_br {
      $floating_range_br = hiera('CONFIG_PROVISION_TEMPEST_FLOATRANGE')
    }

    class { '::neutron::keystone::authtoken':
      username     => 'neutron',
      password     => $neutron_user_password,
      auth_uri     => hiera('CONFIG_KEYSTONE_PUBLIC_URL_VERSIONLESS'),
      auth_url     => hiera('CONFIG_KEYSTONE_ADMIN_URL'),
      project_name => 'services',
    }

    if $provision_neutron_br and $setup_ovs_bridge {
      Neutron_config<||> -> Neutron_l3_ovs_bridge['demo_bridge']
      neutron_l3_ovs_bridge { 'demo_bridge':
        name        => $public_bridge_name,
        ensure      => present,
        subnet_name => 'public_subnet',
      }

      firewall { '000 nat':
        chain    => 'POSTROUTING',
        jump     => 'MASQUERADE',
        source   => $floating_range_br,
        outiface => $::gateway_device,
        table    => 'nat',
        proto    => 'all',
      }


      if $public_bridge_name != '' {
        firewall { '000 forward out':
          chain    => 'FORWARD',
          action   => 'accept',
          outiface => $public_bridge_name,
          proto    => 'all',
        }

        firewall { '000 forward in':
          chain   => 'FORWARD',
          action  => 'accept',
          iniface => $public_bridge_name,
          proto   => 'all',
        }
      }
    }
}
