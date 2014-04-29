Firewall <| |> -> Class['nova::compute::libvirt']

# Ensure Firewall changes happen before libvirt service start
# preventing a clash with rules being set by libvirt

if $::is_virtual_packstack == "true" {
    $libvirt_type = "qemu"
    nova_config{
        "DEFAULT/libvirt_cpu_mode": value => "none";
    }
}else{
    $libvirt_type = "kvm"
}

nova_config{
  "DEFAULT/libvirt_inject_partition": value => "-1";
}

case $::operatingsystem {
  'Fedora': {
    $qemu_package = 'qemu-kvm'
  }
  'RedHat', 'CentOS': {
    $qemu_package = 'qemu-kvm-rhev'
  }
  default: {
    $qemu_package = 'qemu-kvm'
  }
}

package { 'qemu-kvm':
  name   => $qemu_package,
  ensure => installed,
}

class { 'nova::compute::libvirt':
  libvirt_type                => "$libvirt_type",
  vncserver_listen            => "%(CONFIG_NOVA_COMPUTE_HOST)s",
}

exec {'load_kvm':
    user => 'root',
    command => '/bin/sh /etc/sysconfig/modules/kvm.modules',
    onlyif => '/usr/bin/test -e /etc/sysconfig/modules/kvm.modules',
}

Class['nova::compute']-> Exec["load_kvm"]

file_line { 'libvirt-guests':
    path  => '/etc/sysconfig/libvirt-guests',
    line  => 'ON_BOOT=ignore',
    match => '^[\s#]*ON_BOOT=.*',
    require => Class['nova::compute::libvirt']
}

# Remove libvirt's default network (usually virbr0) as it's unnecessary and can be confusing
exec {'virsh-net-destroy-default':
    onlyif  => '/usr/bin/virsh net-list | grep default',
    command => '/usr/bin/virsh net-destroy default',
    require => Package['libvirt'],
}

exec {'virsh-net-undefine-default':
    onlyif  => '/usr/bin/virsh net-list --inactive | grep default',
    command => '/usr/bin/virsh net-undefine default',
    require => Exec['virsh-net-destroy-default'],
}
