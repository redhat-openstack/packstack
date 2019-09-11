class packstack::cinder::backend::vmdk ()
{
    cinder::backend::vmdk { 'vmdk':
      host_ip       => hiera('CONFIG_VCENTER_HOST'),
      host_username => hiera('CONFIG_VCENTER_USER'),
      host_password => hiera('CONFIG_VCENTER_PASSWORD'),
    }

    cinder_type { 'vmdk':
      ensure     => present,
      properties => ["volume_backend_name=vmdk"],
      require    => Class['cinder::api'],
    }
}
