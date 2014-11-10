
  ## Images
  ## Glance
  $image_name     = 'cirros'
  $image_source   = hiera('CONFIG_PROVISION_CIRROS_URL')
  $image_ssh_user = 'cirros'

  glance_image { $image_name:
    ensure           => present,
    is_public        => 'yes',
    container_format => 'bare',
    disk_format      => 'qcow2',
    source           => $image_source,
  }

