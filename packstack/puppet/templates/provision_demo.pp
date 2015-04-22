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
  $setup_ovs_bridge          = hiera('CONFIG_PROVISION_ALL_IN_ONE_OVS_BRIDGE')
  $public_bridge_name        = hiera('CONFIG_NEUTRON_L3_EXT_BRIDGE')
  $provision_neutron_avail   = hiera('PROVISION_NEUTRON_AVAILABLE')
  $ip_version                = hiera('CONFIG_IP_VERSION')

  ## Users

  keystone_tenant { $tenant_name:
    ensure      => present,
    enabled     => true,
    description => 'default tenant',
  }
  keystone_user { $username:
    ensure   => present,
    enabled  => true,
    tenant   => $tenant_name,
    password => $password,
  }

  if hiera('CONFIG_HEAT_INSTALL') == 'y' {
    keystone_user_role { "${username}@${tenant_name}":
      ensure => present,
      roles  => ['_member_', 'heat_stack_owner'],
    }
  }

  ## Neutron
  # IPv6 support is not yet available for public network in packstack.  It can
  # be done manually.  Here we just ensure that we don't fail.
  if $provision_neutron_avail and $ip_version != 'ipv6' {
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

    if $setup_ovs_bridge {
      neutron_l3_ovs_bridge { $public_bridge_name:
        ensure      => present,
        subnet_name => $public_subnet_name,
      }
    }
  }

if $setup_ovs_bridge and $ip_version != 'ipv6' {
  firewall { '000 nat':
    chain    => 'POSTROUTING',
    jump     => 'MASQUERADE',
    source   => hiera('CONFIG_PROVISION_DEMO_FLOATRANGE'),
    outiface => $::gateway_device,
    table    => 'nat',
    proto    => 'all',
  }

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
