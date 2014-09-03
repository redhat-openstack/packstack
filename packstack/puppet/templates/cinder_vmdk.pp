cinder::backend::vmdk { 'vmdk':
  host_ip       => "%(CONFIG_VCENTER_HOST)s",
  host_username => "%(CONFIG_VCENTER_USER)s",
  host_password => "%(CONFIG_VCENTER_PASSWORD)s",
}

cinder::type { 'vmdk':
  set_key   => 'volume_backend_name',
  set_value => 'vmdk',
  require   => Class['cinder::api'],
}
