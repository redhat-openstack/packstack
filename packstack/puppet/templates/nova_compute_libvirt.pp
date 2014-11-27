Firewall <| |> -> Class['nova::compute::libvirt']

# Ensure Firewall changes happen before libvirt service start
# preventing a clash with rules being set by libvirt

if $::is_virtual == 'true' {
  $libvirt_virt_type = 'qemu'
  $libvirt_cpu_mode = 'none'
} else {
  $libvirt_virt_type = 'kvm'
}

nova_config{
  'libvirt/inject_partition': value => '-1';
}

# We need to preferably install qemu-kvm-rhev
exec { 'qemu-kvm':
  path    => '/usr/bin',
  command => 'yum install -y -d 0 -e 0 qemu-kvm',
  onlyif  => 'yum install -y -d 0 -e 0 qemu-kvm-rhev &> /dev/null && exit 1 || exit 0',
  before  => Class['nova::compute::libvirt'],
}

class { 'nova::compute::libvirt':
  libvirt_virt_type => $libvirt_virt_type,
  libvirt_cpu_mode  => $libvirt_cpu_mode,
  vncserver_listen  => '0.0.0.0',
  migration_support => true,
}

exec { 'load_kvm':
  user    => 'root',
  command => '/bin/sh /etc/sysconfig/modules/kvm.modules',
  onlyif  => '/usr/bin/test -e /etc/sysconfig/modules/kvm.modules',
}

Class['nova::compute'] -> Exec['load_kvm']

file_line { 'libvirt-guests':
  path    => '/etc/sysconfig/libvirt-guests',
  line    => 'ON_BOOT=ignore',
  match   => '^[\s#]*ON_BOOT=.*',
  require => Class['nova::compute::libvirt'],
}

# Remove libvirt's default network (usually virbr0) as it's unnecessary and
# can be confusing
exec {'virsh-net-destroy-default':
  onlyif  => '/usr/bin/virsh net-list | grep default',
  command => '/usr/bin/virsh net-destroy default',
  require => Service['libvirt'],
}

exec {'virsh-net-undefine-default':
  onlyif  => '/usr/bin/virsh net-list --inactive | grep default',
  command => '/usr/bin/virsh net-undefine default',
  require => Exec['virsh-net-destroy-default'],
}
