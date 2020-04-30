class packstack::manila::backend::generic ()
{
    ensure_packages(['nfs-utils'], {'ensure' => 'present'})

    manila::backend::generic{ 'generic':
      driver_handles_share_servers => hiera('CONFIG_MANILA_GENERIC_DRV_HANDLES_SHARE_SERVERS'),
      volume_name_template         => hiera('CONFIG_MANILA_GENERIC_VOLUME_NAME_TEMPLATE'),
      share_mount_path             => hiera('CONFIG_MANILA_GENERIC_SHARE_MOUNT_PATH'),
    }

    packstack::manila::network{ 'generic': }

    $admin_username = hiera('CONFIG_KEYSTONE_ADMIN_USERNAME')
    $admin_password = hiera('CONFIG_KEYSTONE_ADMIN_PW')
    $admin_tenant   = 'admin'
    $keystone_url   = hiera('CONFIG_KEYSTONE_PUBLIC_URL')

    nova_flavor { 'm1.manila':
      ensure  => present,
      id      => '66',
      ram     => '512',
      disk    => '1',
      vcpus   => '1',
      require => [ Class['::nova::api'], Class['::nova::keystone::auth'] ],
    }
    -> manila::service_instance{ 'generic':
      service_image_location     => hiera('CONFIG_MANILA_SERVICE_IMAGE_LOCATION'),
      service_instance_user      => hiera('CONFIG_MANILA_SERVICE_INSTANCE_USER'),
      service_instance_password  => hiera('CONFIG_MANILA_SERVICE_INSTANCE_PASSWORD'),
      service_instance_flavor_id => 66,
    }

    class { '::manila::compute::nova':
      auth_type => 'password',
      auth_url  => hiera('CONFIG_KEYSTONE_PUBLIC_URL_VERSIONLESS'),
      password  => hiera('CONFIG_NOVA_KS_PW'),
    }

    class { '::manila::volume::cinder':
      auth_type => 'password',
      auth_url  => hiera('CONFIG_KEYSTONE_PUBLIC_URL_VERSIONLESS'),
      password  => hiera('CONFIG_CINDER_KS_PW'),
    }
}
