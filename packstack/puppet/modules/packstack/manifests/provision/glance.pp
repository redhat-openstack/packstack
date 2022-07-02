class packstack::provision::glance ()
{
    $image_name               = lookup('CONFIG_PROVISION_IMAGE_NAME')
    $image_source             = lookup('CONFIG_PROVISION_IMAGE_URL')
    $image_format             = lookup('CONFIG_PROVISION_IMAGE_FORMAT')
    $image_properties         = lookup('CONFIG_PROVISION_IMAGE_PROPERTIES')

    glance_image { $image_name:
      ensure           => present,
      is_public        => 'yes',
      container_format => 'bare',
      disk_format      => $image_format,
      source           => $image_source,
      properties       => $image_properties
    }
}
