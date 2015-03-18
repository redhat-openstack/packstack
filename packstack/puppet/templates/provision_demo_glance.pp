
  ## Images
  ## Glance
  $image_name     = hiera('CONFIG_PROVISION_IMAGE_NAME')
  $image_source   = hiera('CONFIG_PROVISION_IMAGE_URL')
  $image_ssh_user = hiera('CONFIG_PROVISION_IMAGE_SSH_USER')
  $image_format   = hiera('CONFIG_PROVISION_IMAGE_FORMAT')

  glance_image { $image_name:
    ensure           => present,
    is_public        => 'yes',
    container_format => 'bare',
    disk_format      => $image_format,
    source           => $image_source,
  }
