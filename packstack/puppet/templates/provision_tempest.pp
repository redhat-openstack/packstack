
if '%(CONFIG_PROVISION_TEMPEST_USER)s' != '' {
  ## Keystone
  # non admin user
  $username                  = '%(CONFIG_PROVISION_TEMPEST_USER)s'

  if '%(CONFIG_PROVISION_TEMPEST_USER)s' == 'demo' and
     '%(CONFIG_PROVISION_DEMO)s' == 'y' {
    $password = '%(CONFIG_KEYSTONE_DEMO_PW)s'
  } else {
    $password = '%(CONFIG_PROVISION_TEMPEST_USER_PW)s'
  }

  $tenant_name               = '%(CONFIG_PROVISION_TEMPEST_USER)s'
  # admin user
  $admin_username            = 'admin'
  $admin_password            = '%(CONFIG_KEYSTONE_ADMIN_PW)s'
  $admin_tenant_name         = 'admin'

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
  $public_bridge_name        = '%(CONFIG_PROVISION_DEMO_FLOATRANGE)s'

  ## Tempest
  $configure_tempest         = %(CONFIG_PROVISION_TEMPEST)s

  $image_name_alt            = false
  $image_source_alt          = false
  $image_ssh_user_alt        = false

  $identity_uri              = undef
  $tempest_repo_uri          = '%(CONFIG_PROVISION_TEMPEST_REPO_URI)s'
  $tempest_repo_revision     = '%(CONFIG_PROVISION_TEMPEST_REPO_REVISION)s'
  $tempest_clone_path        = '/var/lib/tempest'
  $tempest_clone_owner       = 'root'
  $setup_venv                = false
  $resize_available          = undef
  $change_password_available = undef
  $cinder_available          = undef
  $glance_available          = true
  $heat_available            = undef
  $horizon_available         = undef
  $neutron_available         = %(PROVISION_NEUTRON_AVAILABLE)s
  $nova_available            = true
  $swift_available           = undef

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

  keystone_tenant { $alt_tenant_name:
    ensure      => present,
    enabled     => true,
    description => 'alt tenant',
  }

  keystone_user { $alt_username:
    ensure      => present,
    enabled     => true,
    tenant      => $alt_tenant_name,
    password    => $alt_password,
  }

  ## Images

  glance_image { $image_name:
    ensure           => present,
    is_public        => 'yes',
    container_format => 'bare',
    disk_format      => 'qcow2',
    source           => $image_source,
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

    glance_image { $image_name_alt:
      ensure           => present,
      is_public        => 'yes',
      container_format => 'bare',
      disk_format      => 'qcow2',
      source           => $image_source_alt_real,
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

  ## Tempest

  if $configure_tempest {
    $tempest_requires = concat([
                                Keystone_user[$username],
                                Keystone_user[$alt_username],
                                Glance_image[$image_name],
                                ], $neutron_deps)

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
      alt_username              => $alt_username,
      alt_password              => $alt_password,
      alt_tenant_name           => $alt_tenant_name,
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
} else {
  ## Standalone Tempest installation
  class { 'tempest':
    tempest_repo_uri      => '%(CONFIG_PROVISION_TEMPEST_REPO_URI)s',
    tempest_clone_path    => '/var/lib/tempest',
    tempest_clone_owner   => 'root',
    setup_venv            => false,
    tempest_repo_revision => '%(CONFIG_PROVISION_TEMPEST_REPO_REVISION)s',
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
