  
  ## Images
  ## Glance
  $image_name                = 'cirros'
  $image_source              = 'http://download.cirros-cloud.net/0.3.1/cirros-0.3.1-x86_64-disk.img'
  $image_ssh_user            = 'cirros'

  glance_image { $image_name:
    ensure           => present,
    is_public        => 'yes',
    container_format => 'bare',
    disk_format      => 'qcow2',
    source           => $image_source,
  }

