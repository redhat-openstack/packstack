class packstack::provision::tempest ()
{
    $provision_demo         = str2bool(hiera('CONFIG_PROVISION_DEMO'))
    if $provision_demo {
      $username             = 'demo'
      $password             = hiera('CONFIG_KEYSTONE_DEMO_PW')
      $tenant_name          = 'demo'
      $floating_range       = hiera('CONFIG_PROVISION_DEMO_FLOATRANGE')
    } else {
      $username             = hiera('CONFIG_PROVISION_TEMPEST_USER')
      $password             = hiera('CONFIG_PROVISION_TEMPEST_USER_PW')
      $tenant_name          = 'tempest'
      $floating_range       = hiera('CONFIG_PROVISION_TEMPEST_FLOATRANGE')
    }

    # Authentication/Keystone
    $identity_uri          = regsubst(hiera('CONFIG_KEYSTONE_PUBLIC_URL'), 'v3', 'v2.0')
    $identity_uri_v3       = regsubst(hiera('CONFIG_KEYSTONE_PUBLIC_URL'), 'v2.0', 'v3')
    $auth_version          = regsubst(hiera('CONFIG_KEYSTONE_API_VERSION'), '.0', '')
    $admin_username        = hiera('CONFIG_KEYSTONE_ADMIN_USERNAME')
    $admin_password        = hiera('CONFIG_KEYSTONE_ADMIN_PW')
    $admin_tenant_name     = 'admin'
    $admin_domain_name     = 'Default'

    # get image and network id
    $configure_images          = true
    $configure_networks        = true

    # Image
    $uec_image_name     = hiera('CONFIG_PROVISION_UEC_IMAGE_NAME')
    $image_ssh_user     = hiera('CONFIG_PROVISION_IMAGE_SSH_USER')
    $image_name_alt     = "${uec_image_name}_alt"
    $image_alt_ssh_user = hiera('CONFIG_PROVISION_IMAGE_SSH_USER')
    $image_source       = hiera('CONFIG_PROVISION_IMAGE_URL')
    $image_format       = hiera('CONFIG_PROVISION_IMAGE_FORMAT')

    # network name
    $public_network_name = 'public'

    # nova should be able to resize with packstack setup
    $resize_available          = true

    $change_password_available = undef
    $allow_tenant_isolation    = true
    $dir_log                   = hiera('DIR_LOG')
    $log_file                  = "${dir_log}/tempest.log"
    $use_stderr                = false
    $debug                     = true
    $public_router_id          = undef

    # Tempest
    $tempest_workspace    = '/var/lib/tempest'
    $tempest_user          = hiera('CONFIG_PROVISION_TEMPEST_USER')
    $tempest_password      = hiera('CONFIG_PROVISION_TEMPEST_USER_PW')

    $tempest_flavor_name = hiera('CONFIG_PROVISION_TEMPEST_FLAVOR_NAME')
    $tempest_flavor_ref  = "42"
    $tempest_flavor_ram  = hiera('CONFIG_PROVISION_TEMPEST_FLAVOR_RAM')
    $tempest_flavor_disk = hiera('CONFIG_PROVISION_TEMPEST_FLAVOR_DISK')
    $tempest_flavor_vcpus= hiera('CONFIG_PROVISION_TEMPEST_FLAVOR_VCPUS')

    $tempest_flavor_alt_name = hiera('CONFIG_PROVISION_TEMPEST_FLAVOR_ALT_NAME')
    $tempest_flavor_alt_ref  = "84"
    $tempest_flavor_alt_ram  = hiera('CONFIG_PROVISION_TEMPEST_FLAVOR_ALT_RAM')
    $tempest_flavor_alt_disk = hiera('CONFIG_PROVISION_TEMPEST_FLAVOR_ALT_DISK')
    $tempest_flavor_alt_vcpus= hiera('CONFIG_PROVISION_TEMPEST_FLAVOR_ALT_VCPUS')

    nova_flavor { $tempest_flavor_name :
      ensure => present,
      id     => $tempest_flavor_ref,
      ram    => $tempest_flavor_ram,
      disk   => $tempest_flavor_disk,
      vcpus  => $tempest_flavor_vcpus,
      require => [ Class['::nova::api'], Class['::nova::keystone::auth'] ],
    }
    nova_flavor { $tempest_flavor_alt_name :
      ensure => present,
      id     => $tempest_flavor_alt_ref,
      ram    => $tempest_flavor_alt_ram,
      disk   => $tempest_flavor_alt_disk,
      vcpus  => $tempest_flavor_alt_vcpus,
      require => [ Class['::nova::api'], Class['::nova::keystone::auth'] ],
    }

    # Service availability for testing based on configuration
    $cinder_available     = str2bool(hiera('CONFIG_CINDER_INSTALL'))
    $glance_available     = str2bool(hiera('CONFIG_GLANCE_INSTALL'))
    $horizon_available    = str2bool(hiera('CONFIG_HORIZON_INSTALL'))
    $nova_available       = str2bool(hiera('CONFIG_NOVA_INSTALL'))
    $neutron_available    = str2bool(hiera('CONFIG_NEUTRON_INSTALL'))
    $ceilometer_available = str2bool(hiera('CONFIG_CEILOMETER_INSTALL'))
    $aodh_available       = str2bool(hiera('CONFIG_AODH_INSTALL'))
    $trove_available      = str2bool(hiera('CONFIG_TROVE_INSTALL'))
    $sahara_available     = str2bool(hiera('CONFIG_SAHARA_INSTALL'))
    $heat_available       = str2bool(hiera('CONFIG_HEAT_INSTALL'))
    $swift_available      = str2bool(hiera('CONFIG_SWIFT_INSTALL'))
    $configure_tempest    = str2bool(hiera('CONFIG_PROVISION_TEMPEST'))

    # Some API extensions as l3_agent_scheduler are not enabled by OVN plugin
    $l2_agent  = hiera('CONFIG_NEUTRON_L2_AGENT')
    if $l2_agent == 'ovn' {
      $neutron_api_extensions = 'ext-gw-mode,binding,agent,dhcp_agent_scheduler,external-net,quotas,provider,extraroute,router,extra_dhcp_opt,allowed-address-pairs,security-group,trunk'
    } else {
      $neutron_api_extensions = undef
    }

    class { '::tempest':
      admin_domain_name         => $admin_domain_name,
      admin_password            => $admin_password,
      admin_tenant_name         => $admin_tenant_name,
      admin_username            => $admin_username,
      allow_tenant_isolation    => $allow_tenant_isolation,
      aodh_available            => $aodh_available,
      auth_version              => $auth_version,
      ceilometer_available      => $ceilometer_available,
      cinder_available          => $cinder_available,
      change_password_available => $change_password_available,
      configure_images          => $configure_images,
      configure_networks        => $configure_networks,
      debug                     => $debug,
      flavor_ref                => $tempest_flavor_ref,
      flavor_ref_alt            => $tempest_flavor_alt_ref,
      glance_available          => $glance_available,
      heat_available            => $heat_available,
      horizon_available         => $horizon_available,
      identity_uri              => $identity_uri,
      identity_uri_v3           => $identity_uri_v3,
      keystone_v2               => false,
      image_alt_ssh_user        => $image_alt_ssh_user,
      image_name_alt            => $image_name_alt,
      image_name                => $uec_image_name,
      image_ssh_user            => $image_ssh_user,
      run_ssh                   => true,
      log_file                  => $log_file,
      neutron_available         => $neutron_available,
      nova_available            => $nova_available,
      password                  => $password,
      public_network_name       => $public_network_name,
      public_router_id          => $public_router_id,
      resize_available          => $resize_available,
      sahara_available          => $sahara_available,
      swift_available           => $swift_available,
      tempest_workspace         => $tempest_workspace,
      install_from_source       => false,
      tenant_name               => $tenant_name,
      trove_available           => $trove_available,
      username                  => $username,
      use_stderr                => $use_stderr,
      neutron_api_extensions    => $neutron_api_extensions,
    }

    tempest_config { 'object-storage/operator_role':
      value => 'SwiftOperator',
      path  => "${tempest_workspace}/etc/tempest.conf",
    }
}
