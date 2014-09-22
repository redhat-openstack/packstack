Firewall <| |> -> Class['nova::compute::libvirt']

# Ensure Firewall changes happen before libvirt service start
# preventing a clash with rules being set by libvirt

if $::is_virtual_packstack == "true" {
    $libvirt_virt_type = "qemu"
    $libvirt_cpu_mode = "none"
}else{
    $libvirt_virt_type = "kvm"
}

nova_config{
  "libvirt/inject_partition": value => "-1";
}

exec { 'qemu-kvm':
    path => '/usr/bin',
    command => 'yum install -y qemu-kvm',
    before => Class['nova::compute::libvirt']
}

class { 'nova::compute::libvirt':
    vncserver_listen   => "%(CONFIG_NOVA_COMPUTE_HOST)s",
    libvirt_type       => "$libvirt_virt_type",
    libvirt_cpu_mode   => "$libvirt_cpu_mode",
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
