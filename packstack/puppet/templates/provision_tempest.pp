$provision_tempest_user = hiera('CONFIG_PROVISION_TEMPEST_USER')
$provision_demo         = hiera('CONFIG_PROVISION_DEMO')

if $provision_tempest_user != '' {
  ## Keystone
  # non admin user
  $username                  = $provision_tempest_user

  if $provision_tempest_user == 'demo' and
    $provision_demo == 'y' {
    $password = hiera('CONFIG_KEYSTONE_DEMO_PW')
  } else {
    $password = hiera('CONFIG_PROVISION_TEMPEST_USER_PW')
  }

  $tenant_name               = $provision_tempest_user
  # admin user
  $admin_username            = 'admin'
  $admin_password            = hiera('CONFIG_KEYSTONE_ADMIN_PW')
  $admin_tenant_name         = 'admin'

  ## Glance
  $image_name               = hiera('CONFIG_PROVISION_IMAGE_NAME')
  $image_source             = hiera('CONFIG_PROVISION_IMAGE_URL')
  $image_ssh_user           = hiera('CONFIG_PROVISION_IMAGE_SSH_USER')
  $image_format             = hiera('CONFIG_PROVISION_IMAGE_FORMAT')

  ## Neutron
  $public_network_name       = 'public'
  $public_subnet_name        = 'public_subnet'
  $floating_range            = hiera('CONFIG_PROVISION_DEMO_FLOATRANGE')
  $private_network_name      = 'private'
  $private_subnet_name       = 'private_subnet'
  $fixed_range               = '10.0.0.0/24'
  $router_name               = 'router1'
  $setup_ovs_bridge          = hiera('CONFIG_PROVISION_ALL_IN_ONE_OVS_BRIDGE')
  $public_bridge_name        = hiera('CONFIG_PROVISION_DEMO_FLOATRANGE')

  ## Tempest
  $configure_tempest         = hiera('CONFIG_PROVISION_TEMPEST')

  $image_name_alt            = false
  $image_source_alt          = false
  $image_ssh_user_alt        = false

  $identity_uri              = undef
  $tempest_repo_uri          = hiera('CONFIG_PROVISION_TEMPEST_REPO_URI')
  $tempest_repo_revision     = hiera('CONFIG_PROVISION_TEMPEST_REPO_REVISION')
  $tempest_clone_path        = '/var/lib/tempest'
  $tempest_clone_owner       = 'root'
  $setup_venv                = false
  $resize_available          = undef
  $change_password_available = undef
  $cinder_available          = undef
  $glance_available          = true
  $heat_available            = undef
  $horizon_available         = undef
  $neutron_available         = hiera('PROVISION_NEUTRON_AVAILABLE')
  $nova_available            = true
  $swift_available           = undef

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

  # Support creation of a second glance image
  # distinct from the first, for tempest. It
  # doesn't need to be a different image, just
  # have a different name and ref in glance.
  if $image_name_alt {
    $image_name_alt_real = $image_name_alt
    if ! $image_source_alt {
      # Use the same source by default
      $image_source_alt_real = $image_source
    } else {
      $image_source_alt_real = $image_source_alt
    }

    if ! $image_ssh_user_alt {
      # Use the same user by default
      $image_alt_ssh_user_real = $image_ssh_user
    } else {
      $image_alt_ssh_user_real = $image_ssh_user_alt
    }

  } else {
    $image_name_alt_real = $image_name
  }

  ## Neutron

  if $neutron_available {
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

  ## Tempest

  if $configure_tempest {
    $tempest_requires = concat([Keystone_user[$username]], $neutron_deps)

    class { 'tempest':
      tempest_repo_uri          => $tempest_repo_uri,
      tempest_clone_path        => $tempest_clone_path,
      tempest_clone_owner       => $tempest_clone_owner,
      setup_venv                => $setup_venv,
      tempest_repo_revision     => $tempest_repo_revision,
      image_name                => $image_name,
      image_name_alt            => $image_name_alt_real,
      image_ssh_user            => $image_ssh_user,
      image_alt_ssh_user        => $image_alt_ssh_user_real,
      identity_uri              => $identity_uri,
      username                  => $username,
      password                  => $password,
      tenant_name               => $tenant_name,
      admin_username            => $admin_username,
      admin_password            => $admin_password,
      admin_tenant_name         => $admin_tenant_name,
      public_network_name       => $public_network_name,
      resize_available          => $resize_available,
      change_password_available => $change_password_available,
      cinder_available          => $cinder_available,
      glance_available          => $glance_available,
      heat_available            => $heat_available,
      horizon_available         => $horizon_available,
      neutron_available         => $neutron_available,
      nova_available            => $nova_available,
      swift_available           => $swift_available,
      require                   => $tempest_requires,
    }
  }

  if hiera('CONFIG_PROVISION_ALL_IN_ONE_OVS_BRIDGE') {
    firewall { '000 nat':
      chain    => 'POSTROUTING',
      jump     => 'MASQUERADE',
      source   => hiera('CONFIG_PROVISION_TEMPEST_FLOATRANGE'),
      outiface => $::gateway_device,
      table    => 'nat',
      proto    => 'all',
    }

    firewall { '000 forward out':
      chain    => 'FORWARD',
      action   => 'accept',
      outiface => hiera('CONFIG_NEUTRON_L3_EXT_BRIDGE'),
      proto    => 'all',
    }

    firewall { '000 forward in':
      chain   => 'FORWARD',
      action  => 'accept',
      iniface => hiera('CONFIG_NEUTRON_L3_EXT_BRIDGE'),
      proto   => 'all',
    }
  }
} else {
  ## Standalone Tempest installation
  class { 'tempest':
    tempest_repo_uri      => hiera('CONFIG_PROVISION_TEMPEST_REPO_URI'),
    tempest_clone_path    => '/var/lib/tempest',
    tempest_clone_owner   => 'root',
    setup_venv            => false,
    tempest_repo_revision => hiera('CONFIG_PROVISION_TEMPEST_REPO_REVISION'),
    configure_images      => false,
    configure_networks    => false,
    cinder_available      => undef,
    glance_available      => true,
    heat_available        => undef,
    horizon_available     => undef,
    neutron_available     => false,
    nova_available        => true,
    swift_available       => undef,
  }
}
