  ## Keystone
  # non admin user
  $username                  = 'demo'
  $password                  = hiera('CONFIG_KEYSTONE_DEMO_PW')
  $tenant_name               = 'demo'
  # admin user
  $admin_username            = hiera('CONFIG_KEYSTONE_ADMIN_USERNAME')
  $admin_password            = hiera('CONFIG_KEYSTONE_ADMIN_PW')
  $admin_tenant_name         = 'admin'

  ## Neutron
  $public_network_name       = 'public'
  $public_subnet_name        = 'public_subnet'
  $floating_range            = hiera('CONFIG_PROVISION_DEMO_FLOATRANGE')
  $private_network_name      = 'private'
  $private_subnet_name       = 'private_subnet'
  $fixed_range               = '10.0.0.0/24'
  $router_name               = 'router1'
  $provision_neutron_avail   = hiera('PROVISION_NEUTRON_AVAILABLE')

  ## Users

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

  if hiera('CONFIG_HEAT_INSTALL') == 'y' {
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
  if $provision_neutron_avail {
    $neutron_deps = [Neutron_network[$public_network_name]]

    neutron_network { $public_network_name:
      ensure          => present,
      router_external => true,
      tenant_name     => $admin_tenant_name,
    }
    neutron_subnet { $public_subnet_name:
      ensure       => 'present',
      cidr         => $floating_range,
      enable_dhcp  => false,
      network_name => $public_network_name,
      tenant_name  => $admin_tenant_name,
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
