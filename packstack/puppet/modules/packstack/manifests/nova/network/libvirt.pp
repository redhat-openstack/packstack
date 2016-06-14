class packstack::nova::network::libvirt ()
{
    $vmware_backend = hiera('CONFIG_VMWARE_BACKEND')

    if $vmware_backend == 'n' {
      exec { 'libvirtd_reload':
        path      => ['/usr/sbin/', '/sbin', '/usr/bin/'],
        command   => 'systemctl restart libvirtd',
        logoutput => 'on_failure',
        require   => Class['::packstack::nova::compute::libvirt'],
      }
    }
}
