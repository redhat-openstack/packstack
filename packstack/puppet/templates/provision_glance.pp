$image_name     = hiera('CONFIG_PROVISION_IMAGE_NAME')
$image_source   = hiera('CONFIG_PROVISION_IMAGE_URL')
$image_format   = hiera('CONFIG_PROVISION_IMAGE_FORMAT')

glance_image { $image_name:
  ensure           => present,
  is_public        => 'yes',
  container_format => 'bare',
  disk_format      => $image_format,
  source           => $image_source,
}

if str2bool(hiera('CONFIG_PROVISION_TEMPEST')) {
  $image_name_alt        = "${image_name}_alt"
  glance_image { $image_name_alt:
    ensure           => present,
    is_public        => 'yes',
    container_format => 'bare',
    disk_format      => $image_format,
    source           => $image_source,
  }
}
