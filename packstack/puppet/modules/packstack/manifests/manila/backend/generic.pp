class packstack::manila::backend::generic ()
{
    ensure_packages(['nfs-utils'], {'ensure' => 'present'})

    manila::backend::generic{ 'generic':
      driver_handles_share_servers => lookup('CONFIG_MANILA_GENERIC_DRV_HANDLES_SHARE_SERVERS'),
      volume_name_template         => lookup('CONFIG_MANILA_GENERIC_VOLUME_NAME_TEMPLATE'),
      share_mount_path             => lookup('CONFIG_MANILA_GENERIC_SHARE_MOUNT_PATH'),
    }

    packstack::manila::network{ 'generic': }

    $admin_username = lookup('CONFIG_KEYSTONE_ADMIN_USERNAME')
    $admin_password = lookup('CONFIG_KEYSTONE_ADMIN_PW')
    $admin_tenant   = 'admin'
    $keystone_url   = lookup('CONFIG_KEYSTONE_PUBLIC_URL')

    nova_flavor { 'm1.manila':
      ensure  => present,
      id      => '66',
      ram     => '512',
      disk    => '1',
      vcpus   => '1',
      require => [ Class['::nova::api'], Class['::nova::keystone::auth'] ],
    }
    -> manila::backend::service_instance{ 'generic':
      service_image_location     => lookup('CONFIG_MANILA_SERVICE_IMAGE_LOCATION'),
      service_instance_user      => lookup('CONFIG_MANILA_SERVICE_INSTANCE_USER'),
      service_instance_password  => lookup('CONFIG_MANILA_SERVICE_INSTANCE_PASSWORD'),
      service_instance_flavor_id => 66,
    }

    class { 'manila::compute::nova':
      auth_type => 'password',
      auth_url  => lookup('CONFIG_KEYSTONE_PUBLIC_URL_VERSIONLESS'),
      password  => lookup('CONFIG_NOVA_KS_PW'),
    }

    class { 'manila::volume::cinder':
      auth_type => 'password',
      auth_url  => lookup('CONFIG_KEYSTONE_PUBLIC_URL_VERSIONLESS'),
      password  => lookup('CONFIG_CINDER_KS_PW'),
    }
}
