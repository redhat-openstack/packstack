  ## Keystone
  # non admin user
  $username                  = 'demo'
  $password                  = '%(CONFIG_KEYSTONE_DEMO_PW)s'
  $tenant_name               = 'demo'
  # admin user
  $admin_username            = 'admin'
  $admin_password            = '%(CONFIG_KEYSTONE_ADMIN_PW)s'
  $admin_tenant_name         = 'admin'

  # Heat Using Trusts
  $heat_using_trusts         = '%(CONFIG_HEAT_USING_TRUSTS)s'

  ## Glance
  $image_name                = 'cirros'
  $image_source              = 'http://download.cirros-cloud.net/0.3.1/cirros-0.3.1-x86_64-disk.img'
  $image_ssh_user            = 'cirros'

  ## Neutron
  $public_network_name       = 'public'
  $public_subnet_name        = 'public_subnet'
  $floating_range            = '%(CONFIG_PROVISION_DEMO_FLOATRANGE)s'
  $private_network_name      = 'private'
  $private_subnet_name       = 'private_subnet'
  $fixed_range               = '10.0.0.0/24'
  $router_name               = 'router1'
  $setup_ovs_bridge          = %(CONFIG_PROVISION_ALL_IN_ONE_OVS_BRIDGE)s
  $public_bridge_name        = '%(CONFIG_NEUTRON_L3_EXT_BRIDGE)s'

  ## Users

  keystone_tenant { $tenant_name:
    ensure      => present,
    enabled     => true,
    description => 'default tenant',
  }
  keystone_user { $username:
    ensure      => present,
    enabled     => true,
    tenant      => $tenant_name,
    password    => $password,
  }

  if $heat_using_trusts == 'y' {
    keystone_user_role { "${username}@${tenant_name}":
      ensure  => present,
      roles   => ['_member_', 'heat_stack_owner'],
    }
  }

  ## Images

  glance_image { $image_name:
    ensure           => present,
    is_public        => 'yes',
    container_format => 'bare',
    disk_format      => 'qcow2',
    source           => $image_source,
  }

  ## Neutron

  if %(PROVISION_NEUTRON_AVAILABLE)s {
    $neutron_deps = [Neutron_network[$public_network_name]]

    neutron_network { $public_network_name:
      ensure          => present,
      router_external => true,
      tenant_name     => $admin_tenant_name,
    }
    neutron_subnet { $public_subnet_name:
      ensure          => 'present',
      cidr            => $floating_range,
      enable_dhcp     => false,
      network_name    => $public_network_name,
      tenant_name     => $admin_tenant_name,
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

if %(CONFIG_PROVISION_ALL_IN_ONE_OVS_BRIDGE)s {
  firewall { '000 nat':
    chain  => 'POSTROUTING',
    jump   => 'MASQUERADE',
    source => $::openstack::provision::floating_range,
    outiface => $::gateway_device,
    table => 'nat',
    proto => 'all',
  }

  firewall { '000 forward out':
    chain => 'FORWARD',
    action  => 'accept',
    outiface => '%(CONFIG_NEUTRON_L3_EXT_BRIDGE)s',
    proto => 'all',
  }

  firewall { '000 forward in':
    chain => 'FORWARD',
    action  => 'accept',
    iniface => '%(CONFIG_NEUTRON_L3_EXT_BRIDGE)s',
    proto => 'all',
  }
}
