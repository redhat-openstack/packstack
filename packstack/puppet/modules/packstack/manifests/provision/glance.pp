class packstack::provision::glance ()
{
    $image_name               = hiera('CONFIG_PROVISION_IMAGE_NAME')
    $image_source             = hiera('CONFIG_PROVISION_IMAGE_URL')
    $image_format             = hiera('CONFIG_PROVISION_IMAGE_FORMAT')
    $image_properties         = hiera('CONFIG_PROVISION_IMAGE_PROPERTIES')

    glance_image { $image_name:
      ensure           => present,
      is_public        => 'yes',
      container_format => 'bare',
      disk_format      => $image_format,
      source           => $image_source,
      properties       => $image_properties
    }
}
