$image_name               = hiera('CONFIG_PROVISION_IMAGE_NAME')
$image_source             = hiera('CONFIG_PROVISION_IMAGE_URL')
$image_format             = hiera('CONFIG_PROVISION_IMAGE_FORMAT')
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

  glance_image{$uec_image_name:
    ensure           => present,
    is_public        => 'yes',
    container_format => 'ami',
    disk_format      => 'ami',
    source           => $uec_image_source_disk,
    properties       => { 'kernel_id' => '146d4a6b-ad1e-4d9f-8b08-98eae3c3dab4', 'ramdisk_id' => '0b50e2e5-1440-4654-b568-4e120ddf28c1' },
    require          => [ Glance_image["${uec_image_name}-kernel"], Glance_image["${uec_image_name}-ramdisk"] ]
  }

  glance_image{$image_name_alt:
    ensure           => present,
    is_public        => 'yes',
    container_format => 'ami',
    disk_format      => 'ami',
    source           => $uec_image_source_disk,
    properties       => { 'kernel_id' => '146d4a6b-ad1e-4d9f-8b08-98eae3c3dab4', 'ramdisk_id' => '0b50e2e5-1440-4654-b568-4e120ddf28c1' },
    require          => [ Glance_image["${uec_image_name}-kernel"], Glance_image["${uec_image_name}-ramdisk"] ]
  }

}
