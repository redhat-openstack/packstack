class packstack::provision::bridge ()
{
    $provision_neutron_br    = str2bool(lookup('CONFIG_NEUTRON_INSTALL'))
    $setup_ovs_bridge        = str2bool(lookup('CONFIG_PROVISION_OVS_BRIDGE'))
    $public_bridge_name      = lookup('CONFIG_NEUTRON_L3_EXT_BRIDGE', undef, undef, 'br-ex')
    $provision_tempest_br    = str2bool(lookup('CONFIG_PROVISION_TEMPEST'))
    $provision_demo_br       = str2bool(lookup('CONFIG_PROVISION_DEMO'))

    $neutron_user_password   = lookup('CONFIG_NEUTRON_KS_PW')

    if $provision_demo_br {
      $floating_range_br = lookup('CONFIG_PROVISION_DEMO_FLOATRANGE')
    } elsif $provision_tempest_br {
      $floating_range_br = lookup('CONFIG_PROVISION_TEMPEST_FLOATRANGE')
    }

    if $provision_neutron_br and $setup_ovs_bridge {
      Neutron_config<||> -> Neutron_l3_ovs_bridge['demo_bridge']
      neutron_l3_ovs_bridge { 'demo_bridge':
        ensure      => present,
        name        => $public_bridge_name,
        subnet_name => 'public_subnet',
      }

      firewall { '000 nat':
        chain    => 'POSTROUTING',
        jump     => 'MASQUERADE',
        source   => $floating_range_br,
        outiface => $facts['gateway_device'],
        table    => 'nat',
        proto    => 'all',
      }


      if $public_bridge_name != '' {
        firewall { '000 forward out':
          chain    => 'FORWARD',
          jump     => 'accept',
          outiface => $public_bridge_name,
          proto    => 'all',
        }

        firewall { '000 forward in':
          chain   => 'FORWARD',
          jump    => 'accept',
          iniface => $public_bridge_name,
          proto   => 'all',
        }
      }
    }
}
