$vmware_backend = '%(CONFIG_VMWARE_BACKEND)s'
if $vmware_backend == 'n' {
  exec { 'libvirtd_restart':
    path => ['/usr/sbin/', '/sbin'],
    command => 'service libvirtd restart',
    logoutput => 'on_failure',
    require => Class['nova::network'],
  }
}
