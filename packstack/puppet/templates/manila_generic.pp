
package { 'nfs-utils': ensure => present }

manila::backend::generic{ 'generic':
  volume_name_template => hiera('CONFIG_MANILA_GENERIC_VOLUME_NAME_TEMPLATE'),
  share_mount_path     => hiera('CONFIG_MANILA_GENERIC_SHARE_MOUNT_PATH'),
}

manila::service_instance{ 'generic':
  service_image_location    => hiera('CONFIG_MANILA_SERVICE_IMAGE_LOCATION'),
  service_instance_user     => hiera('CONFIG_MANILA_SERVICE_INSTANCE_USER'),
  service_instance_password => hiera('CONFIG_MANILA_SERVICE_INSTANCE_PASSWORD'),
}

class { 'manila::compute::nova':
  nova_admin_password    => hiera('CONFIG_NOVA_KS_PW'),
  nova_admin_tenant_name => 'services',
}

class { 'manila::volume::cinder':
  cinder_admin_password    => hiera('CONFIG_CINDER_KS_PW'),
  cinder_admin_tenant_name => 'services',
}
