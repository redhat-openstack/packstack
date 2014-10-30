$vmware_backend = hiera('CONFIG_VMWARE_BACKEND')

if $vmware_backend == 'n' {
  exec { 'libvirtd_reload':
    path      => ['/usr/sbin/', '/sbin'],
    command   => 'service libvirtd reload',
    logoutput => 'on_failure',
    require   => Class['nova::network'],
  }
}
