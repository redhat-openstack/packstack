class packstack::provision ()
{
    $provision_demo            = str2bool(lookup('CONFIG_PROVISION_DEMO'))
    $provision_tempest         = str2bool(lookup('CONFIG_PROVISION_TEMPEST'))
    $provision_neutron         = str2bool(lookup('CONFIG_NEUTRON_INSTALL'))
    $heat_available            = str2bool(lookup('CONFIG_HEAT_INSTALL'))

    if $provision_demo {
      $username             = 'demo'
      $password             = lookup('CONFIG_KEYSTONE_DEMO_PW')
      $project_name         = 'demo'
      $floating_range       = lookup('CONFIG_PROVISION_DEMO_FLOATRANGE')
      $allocation_pools     = lookup('CONFIG_PROVISION_DEMO_ALLOCATION_POOLS')
    } elsif $provision_tempest {
      $username             = lookup('CONFIG_PROVISION_TEMPEST_USER')
      $password             = lookup('CONFIG_PROVISION_TEMPEST_USER_PW')
      $project_name         = 'tempest'
      $floating_range       = lookup('CONFIG_PROVISION_TEMPEST_FLOATRANGE')
      $allocation_pools     = []
      if (empty($username) or empty($password)) {
        fail("Both CONFIG_PROVISION_TEMPEST_USER and
        CONFIG_PROVISION_TEMPEST_USER_PW need to be configured.")
      }
    }

    if $provision_demo or $provision_tempest {

      # Keystone
      $admin_project_name = 'admin'
      keystone_tenant { $project_name:
        ensure      => present,
        enabled     => true,
        description => 'default tenant',
      }

      keystone_user { $username:
        ensure   => present,
        enabled  => true,
        password => $password,
      }

      keystone_user_role { "${username}@${project_name}":
        ensure => present,
        roles  => ['member'],
      }

      ## Neutron
      if $provision_neutron {
        $public_network_name  = 'public'
        $public_subnet_name   = 'public_subnet'
        $private_network_name = 'private'
        $private_subnet_name  = 'private_subnet'
        $fixed_range          = '10.0.0.0/24'
        $router_name          = 'router1'
        $public_physnet       = lookup('CONFIG_NEUTRON_OVS_EXTERNAL_PHYSNET')

        $neutron_deps = [Neutron_network[$public_network_name]]

        neutron_network { $public_network_name:
          ensure                    => present,
          router_external           => true,
          project_name              => $admin_project_name,
          provider_network_type     => 'flat',
          provider_physical_network => $public_physnet,
        }
        neutron_subnet { $public_subnet_name:
          ensure           => 'present',
          cidr             => $floating_range,
          allocation_pools => $allocation_pools,
          enable_dhcp      => false,
          network_name     => $public_network_name,
          project_name     => $admin_project_name,
        }
        neutron_network { $private_network_name:
          ensure       => present,
          project_name => $project_name,
        }
        neutron_subnet { $private_subnet_name:
          ensure        => present,
          cidr          => $fixed_range,
          network_name  => $private_network_name,
          project_name  => $project_name,
        }
        # Tenant-owned router - assumes network namespace isolation
        neutron_router { $router_name:
          ensure               => present,
          project_name         => $project_name,
          gateway_network_name => $public_network_name,
          # A neutron_router resource must explicitly declare a dependency on
          # the first subnet of the gateway network.
          require              => Neutron_subnet[$public_subnet_name],
        }
        neutron_router_interface { "${router_name}:${private_subnet_name}":
          ensure => present,
        }
      }
    }
}
