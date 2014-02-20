class { 'cinder::volume::vmdk':
  host_ip       => "%(CONFIG_VCENTER_HOST)s",
  host_username => "%(CONFIG_VCENTER_USER)s",
  host_password => "%(CONFIG_VCENTER_PASSWORD)s",
}
