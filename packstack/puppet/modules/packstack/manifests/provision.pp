class packstack::provision ()
{
    $provision_demo            = str2bool(hiera('CONFIG_PROVISION_DEMO'))
    $provision_tempest         = str2bool(hiera('CONFIG_PROVISION_TEMPEST'))
    $provision_neutron         = str2bool(hiera('CONFIG_NEUTRON_INSTALL'))
    $heat_available            = str2bool(hiera('CONFIG_HEAT_INSTALL'))

    if $provision_demo {
      $username             = 'demo'
      $password             = hiera('CONFIG_KEYSTONE_DEMO_PW')
      $tenant_name          = 'demo'
      $floating_range       = hiera('CONFIG_PROVISION_DEMO_FLOATRANGE')
      $allocation_pools     = hiera(
                              'CONFIG_PROVISION_DEMO_ALLOCATION_POOLS')
    } elsif $provision_tempest {
      $username             = hiera('CONFIG_PROVISION_TEMPEST_USER')
      $password             = hiera('CONFIG_PROVISION_TEMPEST_USER_PW')
      $tenant_name          = 'tempest'
      $floating_range       = hiera('CONFIG_PROVISION_TEMPEST_FLOATRANGE')
      $allocation_pools     = []
      if (empty($tempest_user) or empty($tempest_password)) {
        fail("Both CONFIG_PROVISION_TEMPEST_USER and
        CONFIG_PROVISION_TEMPEST_USER_PW need to be configured.")
      }
    }

    if $provision_demo or $provision_tempest {

      # Keystone
      $admin_tenant_name = 'admin'
      keystone_tenant { $tenant_name:
        ensure      => present,
        enabled     => true,
        description => 'default tenant',
      }

      keystone_user { $username:
        ensure   => present,
        enabled  => true,
        password => $password,
      }

      if $heat_available {
        keystone_user_role { "${username}@${tenant_name}":
          ensure => present,
          roles  => ['_member_', 'heat_stack_owner'],
        }
      } else {
        keystone_user_role { "${username}@${tenant_name}":
          ensure => present,
          roles  => ['_member_'],
        }
      }

      ## Neutron
      if $provision_neutron {
        $public_network_name  = 'public'
        $public_subnet_name   = 'public_subnet'
        $private_network_name = 'private'
        $private_subnet_name  = 'private_subnet'
        $fixed_range          = '10.0.0.0/24'
        $router_name          = 'router1'
        $public_physnet       = hiera('CONFIG_NEUTRON_OVS_EXTERNAL_PHYSNET')

        $neutron_deps = [Neutron_network[$public_network_name]]

        neutron_network { $public_network_name:
          ensure                    => present,
          router_external           => true,
          tenant_name               => $admin_tenant_name,
          provider_network_type     => 'flat',
          provider_physical_network => $public_physnet,
        }
        neutron_subnet { $public_subnet_name:
          ensure           => 'present',
          cidr             => $floating_range,
          allocation_pools => $allocation_pools,
          enable_dhcp      => false,
          network_name     => $public_network_name,
          tenant_name      => $admin_tenant_name,
        }
        neutron_network { $private_network_name:
          ensure      => present,
          tenant_name => $tenant_name,
        }
        neutron_subnet { $private_subnet_name:
          ensure       => present,
          cidr         => $fixed_range,
          network_name => $private_network_name,
          tenant_name  => $tenant_name,
        }
        # Tenant-owned router - assumes network namespace isolation
        neutron_router { $router_name:
          ensure               => present,
          tenant_name          => $tenant_name,
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
