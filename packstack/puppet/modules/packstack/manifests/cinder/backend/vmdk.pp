class packstack::cinder::backend::vmdk ()
{
    cinder::backend::vmdk { 'vmdk':
      host_ip       => hiera('CONFIG_VCENTER_HOST'),
      host_username => hiera('CONFIG_VCENTER_USER'),
      host_password => hiera('CONFIG_VCENTER_PASSWORD'),
    }

    cinder::type { 'vmdk':
      set_key   => 'volume_backend_name',
      set_value => 'vmdk',
      require   => Class['cinder::api'],
    }
}
