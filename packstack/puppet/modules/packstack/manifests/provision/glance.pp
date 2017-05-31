class packstack::provision::glance ()
{
    $image_name               = hiera('CONFIG_PROVISION_IMAGE_NAME')
    $image_source             = hiera('CONFIG_PROVISION_IMAGE_URL')
    $image_format             = hiera('CONFIG_PROVISION_IMAGE_FORMAT')
    $image_properties         = hiera('CONFIG_PROVISION_IMAGE_PROPERTIES')
    $uec_image_name           = hiera('CONFIG_PROVISION_UEC_IMAGE_NAME')
    $uec_image_source_kernel  = hiera('CONFIG_PROVISION_UEC_IMAGE_KERNEL_URL')
    $uec_image_source_ramdisk = hiera('CONFIG_PROVISION_UEC_IMAGE_RAMDISK_URL')
    $uec_image_source_disk    = hiera('CONFIG_PROVISION_UEC_IMAGE_DISK_URL')

    glance_image { $image_name:
      ensure           => present,
      is_public        => 'yes',
      container_format => 'bare',
      disk_format      => $image_format,
      source           => $image_source,
      properties       => $image_properties
    }

    if str2bool(hiera('CONFIG_PROVISION_TEMPEST')) {
      $image_name_alt = "${uec_image_name}_alt"

      glance_image{"${uec_image_name}-kernel":
        ensure           => present,
        is_public        => 'yes',
        container_format => 'aki',
        disk_format      => 'aki',
        source           => $uec_image_source_kernel,
        id               => '146d4a6b-ad1e-4d9f-8b08-98eae3c3dab4'
      }

      glance_image{"${uec_image_name}-ramdisk":
        ensure           => present,
        is_public        => 'yes',
        container_format => 'ari',
        disk_format      => 'ari',
        source           => $uec_image_source_ramdisk,
        id               => '0b50e2e5-1440-4654-b568-4e120ddf28c1'
      }
      $uec_properties = { 'kernel_id' => '146d4a6b-ad1e-4d9f-8b08-98eae3c3dab4',
                          'ramdisk_id' => '0b50e2e5-1440-4654-b568-4e120ddf28c1' }
      # Same properties we require for QCOW2 image, we need for UEC image too
      if $image_format == 'qcow2' {
        $image_properties_hash = $image_properties.split(',').map |$tok| { $tok.split('=') }.flatten.hash
        $uec_properties_all = $uec_properties.merge($image_properties_hash)
      } else {
        $uec_properties_all = $uec_properties
      }

      glance_image{$uec_image_name:
        ensure           => present,
        is_public        => 'yes',
        container_format => 'ami',
        disk_format      => 'qcow2',
        source           => $uec_image_source_disk,
        properties       => $uec_properties_all,
        require          => [ Glance_image["${uec_image_name}-kernel"], Glance_image["${uec_image_name}-ramdisk"] ]
      }

      glance_image{$image_name_alt:
        ensure           => present,
        is_public        => 'yes',
        container_format => 'ami',
        # FIXME(jpena): ami used to be an acceptable disk format, but we are
        # failing to boot from volume since https://review.openstack.org/453341
        # because qemu-img convert does not recognize is as a valid format.
        # See https://bugs.launchpad.net/cinder/+bug/1693926
        disk_format      => 'qcow2',
        source           => $uec_image_source_disk,
        properties       => $uec_properties_all,
        require          => [ Glance_image["${uec_image_name}-kernel"], Glance_image["${uec_image_name}-ramdisk"] ]
      }

    }
}
