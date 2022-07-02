class packstack::cinder::backend::vmdk ()
{
    cinder::backend::vmdk { 'vmdk':
      host_ip       => lookup('CONFIG_VCENTER_HOST'),
      host_username => lookup('CONFIG_VCENTER_USER'),
      host_password => lookup('CONFIG_VCENTER_PASSWORD'),
    }

    cinder_type { 'vmdk':
      ensure     => present,
      properties => ['volume_backend_name=vmdk'],
      require    => Class['cinder::api'],
    }
}
