class packstack::provision::tempest ()
{
    $provision_demo         = str2bool(lookup('CONFIG_PROVISION_DEMO'))
    if $provision_demo {
      $username             = 'demo'
      $password             = lookup('CONFIG_KEYSTONE_DEMO_PW')
      $project_name         = 'demo'
      $floating_range       = lookup('CONFIG_PROVISION_DEMO_FLOATRANGE')
    } else {
      $username             = lookup('CONFIG_PROVISION_TEMPEST_USER')
      $password             = lookup('CONFIG_PROVISION_TEMPEST_USER_PW')
      $project_name         = 'tempest'
      $floating_range       = lookup('CONFIG_PROVISION_TEMPEST_FLOATRANGE')
    }

    # Authentication/Keystone
    $identity_uri_v3       = lookup('CONFIG_KEYSTONE_PUBLIC_URL')
    $admin_username        = lookup('CONFIG_KEYSTONE_ADMIN_USERNAME')
    $admin_password        = lookup('CONFIG_KEYSTONE_ADMIN_PW')
    $admin_project_name    = 'admin'
    $admin_domain_name     = 'Default'

    # get image and network id
    $configure_images          = true
    $configure_networks        = true

    # Image
    $image_ssh_user     = lookup('CONFIG_PROVISION_IMAGE_SSH_USER')
    $image_name         = lookup('CONFIG_PROVISION_IMAGE_NAME')
    $image_alt_ssh_user = lookup('CONFIG_PROVISION_IMAGE_SSH_USER')
    $image_source       = lookup('CONFIG_PROVISION_IMAGE_URL')
    $image_format       = lookup('CONFIG_PROVISION_IMAGE_FORMAT')

    # network name
    $public_network_name = 'public'

    # nova should be able to resize with packstack setup
    $resize_available          = true

    $use_dynamic_credentials   = true
    $dir_log                   = lookup('DIR_LOG')
    $log_file                  = "${dir_log}/tempest.log"
    $use_stderr                = false
    $debug                     = true
    $public_router_id          = undef

    # Tempest
    $tempest_workspace    = '/var/lib/tempest'
    $tempest_user          = lookup('CONFIG_PROVISION_TEMPEST_USER')
    $tempest_password      = lookup('CONFIG_PROVISION_TEMPEST_USER_PW')

    $tempest_flavor_name = lookup('CONFIG_PROVISION_TEMPEST_FLAVOR_NAME')
    $tempest_flavor_ref  = '42'
    $tempest_flavor_ram  = lookup('CONFIG_PROVISION_TEMPEST_FLAVOR_RAM')
    $tempest_flavor_disk = lookup('CONFIG_PROVISION_TEMPEST_FLAVOR_DISK')
    $tempest_flavor_vcpus= lookup('CONFIG_PROVISION_TEMPEST_FLAVOR_VCPUS')

    $tempest_flavor_alt_name = lookup('CONFIG_PROVISION_TEMPEST_FLAVOR_ALT_NAME')
    $tempest_flavor_alt_ref  = '84'
    $tempest_flavor_alt_ram  = lookup('CONFIG_PROVISION_TEMPEST_FLAVOR_ALT_RAM')
    $tempest_flavor_alt_disk = lookup('CONFIG_PROVISION_TEMPEST_FLAVOR_ALT_DISK')
    $tempest_flavor_alt_vcpus= lookup('CONFIG_PROVISION_TEMPEST_FLAVOR_ALT_VCPUS')

    nova_flavor { $tempest_flavor_name :
      ensure  => present,
      id      => $tempest_flavor_ref,
      ram     => $tempest_flavor_ram,
      disk    => $tempest_flavor_disk,
      vcpus   => $tempest_flavor_vcpus,
      require => [ Class['::nova::api'], Class['::nova::keystone::auth'] ],
    }
    nova_flavor { $tempest_flavor_alt_name :
      ensure  => present,
      id      => $tempest_flavor_alt_ref,
      ram     => $tempest_flavor_alt_ram,
      disk    => $tempest_flavor_alt_disk,
      vcpus   => $tempest_flavor_alt_vcpus,
      require => [ Class['::nova::api'], Class['::nova::keystone::auth'] ],
    }

    # Service availability for testing based on configuration
    $cinder_available     = str2bool(lookup('CONFIG_CINDER_INSTALL'))
    $glance_available     = str2bool(lookup('CONFIG_GLANCE_INSTALL'))
    $horizon_available    = str2bool(lookup('CONFIG_HORIZON_INSTALL'))
    $nova_available       = str2bool(lookup('CONFIG_NOVA_INSTALL'))
    $neutron_available    = str2bool(lookup('CONFIG_NEUTRON_INSTALL'))
    $ceilometer_available = str2bool(lookup('CONFIG_CEILOMETER_INSTALL'))
    $aodh_available       = str2bool(lookup('CONFIG_AODH_INSTALL'))
    $trove_available      = str2bool(lookup('CONFIG_TROVE_INSTALL'))
    $heat_available       = str2bool(lookup('CONFIG_HEAT_INSTALL'))
    $swift_available      = str2bool(lookup('CONFIG_SWIFT_INSTALL'))
    $configure_tempest    = str2bool(lookup('CONFIG_PROVISION_TEMPEST'))

    # Some API extensions as l3_agent_scheduler are not enabled by OVN plugin
    $l2_agent  = lookup('CONFIG_NEUTRON_L2_AGENT')
    if $l2_agent == 'ovn' {
      $neutron_api_extensions = 'ext-gw-mode,binding,agent,external-net,quotas,provider,extraroute,router,extra_dhcp_opt,allowed-address-pairs,security-group,trunk'
    } else {
      $neutron_api_extensions = undef
    }

    class { 'tempest':
      admin_domain_name         => $admin_domain_name,
      admin_password            => $admin_password,
      admin_project_name        => $admin_project_name,
      admin_username            => $admin_username,
      use_dynamic_credentials   => $use_dynamic_credentials,
      aodh_available            => $aodh_available,
      ceilometer_available      => $ceilometer_available,
      cinder_available          => $cinder_available,
      configure_images          => $configure_images,
      configure_networks        => $configure_networks,
      debug                     => $debug,
      flavor_ref                => $tempest_flavor_ref,
      flavor_ref_alt            => $tempest_flavor_alt_ref,
      glance_available          => $glance_available,
      heat_available            => $heat_available,
      horizon_available         => $horizon_available,
      identity_uri_v3           => $identity_uri_v3,
      image_alt_ssh_user        => $image_alt_ssh_user,
      image_name_alt            => $image_name,
      image_name                => $image_name,
      image_ssh_user            => $image_ssh_user,
      run_ssh                   => true,
      log_file                  => $log_file,
      neutron_available         => $neutron_available,
      nova_available            => $nova_available,
      password                  => $password,
      public_network_name       => $public_network_name,
      public_router_id          => $public_router_id,
      resize_available          => $resize_available,
      swift_available           => $swift_available,
      tempest_workspace         => $tempest_workspace,
      install_from_source       => false,
      project_name              => $project_name,
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
